import logging
import asyncio
from typing import Dict, Any

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import Shop, ShopResult, CommunityInfo, CommunityPage, FloorPlan, Amenity
from apps.targets.models import Target
from utils.ai_integration.service import create_information_gathering_service
from utils.ai_integration.schemas import CommunityInformation
from utils.ai_integration.agent_config import RETRY_CONFIG

logger = logging.getLogger(__name__)


def _parse_and_save_community_info(shop_result: ShopResult, community_info_data: CommunityInformation) -> None:
    """
    Parses the PydanticAI response data and saves it to the CommunityInfo related models.

    Args:
        shop_result: The ShopResult instance to associate the data with
        community_info_data: The CommunityInformation Pydantic model instance
    """
    # Create or update CommunityInfo
    # Using update_or_create to handle potential retries or re-runs
    community_info, created = CommunityInfo.objects.update_or_create(
        shop_result=shop_result,
        defaults={
            'name': community_info_data.name,
            'overview': community_info_data.overview,
            'url': community_info_data.url,
            'application_fee': community_info_data.application_fee,
            'application_fee_source': community_info_data.application_fee_source,
            'administration_fee': community_info_data.administration_fee,
            'administration_fee_source': community_info_data.administration_fee_source,
            'membership_fee': community_info_data.membership_fee,
            'membership_fee_source': community_info_data.membership_fee_source,
            'pet_policy': community_info_data.pet_policy,
            'pet_policy_source': community_info_data.pet_policy_source,
            'self_showings': community_info_data.self_showings,
            'self_showings_source': community_info_data.self_showings_source,
            'office_hours': community_info_data.office_hours,
            'resident_portal_provider': community_info_data.resident_portal_software_provider,
        }
    )
    logger.info(f"{'Created' if created else 'Updated'} CommunityInfo {
                community_info.id} for ShopResult {shop_result.shop_id}")

    # Clear existing related objects before adding new ones to prevent duplicates on update
    community_info.pages.all().delete()
    community_info.floor_plans.all().delete()
    community_info.community_amenities.clear()  # ManyToMany field

    # Create CommunityPage objects
    for page_data in community_info_data.community_pages:
        CommunityPage.objects.create(
            community_info=community_info,
            name=page_data.name,
            overview=page_data.overview,
            url=page_data.url
        )

    # Create FloorPlan objects and their amenities
    for fp_data in community_info_data.floor_plans:
        floor_plan = FloorPlan.objects.create(
            community_info=community_info,
            name=fp_data.name,
            beds=fp_data.beds,
            baths=fp_data.baths,
            url=fp_data.url,
            sqft=fp_data.sqft,
            type=fp_data.type,
            min_rental_price=fp_data.min_rental_price,
            max_rental_price=fp_data.max_rental_price,
            security_deposit=fp_data.security_deposit,
        )
        # Handle floor plan amenities
        for amenity_data in fp_data.floor_plan_amenities:
            if amenity_data.amenity:
                amenity, _ = Amenity.objects.get_or_create(
                    name=amenity_data.amenity)
                floor_plan.amenities.add(amenity)

    # Handle community amenities
    for amenity_data in community_info_data.community_amenities:
        if amenity_data.amenity:
            amenity, _ = Amenity.objects.get_or_create(
                name=amenity_data.amenity)
            community_info.community_amenities.add(amenity)


@shared_task(bind=True, max_retries=RETRY_CONFIG['max_retries'])
def start_information_gathering_task(self, shop_id: str) -> None:
    """
    Celery task to perform AI-driven information gathering for a given Shop using PydanticAI.
    """
    logger.info(f"Starting information gathering task for Shop ID: {shop_id}")

    try:
        shop = Shop.objects.select_related('target').get(id=shop_id)
        target = shop.target
    except Shop.DoesNotExist:
        logger.error(f"Shop with ID {shop_id} not found. Aborting task.")
        return
    except Target.DoesNotExist:
        logger.error(f"Target associated with Shop ID {
                     shop_id} not found. Aborting task.")
        shop.status = Shop.Status.ERROR
        shop.end_time = timezone.now()
        shop.save(update_fields=['status', 'end_time', 'updated_at'])
        return

    # Update shop status to IN_PROGRESS
    shop.status = Shop.Status.IN_PROGRESS
    shop.start_time = timezone.now()
    shop.save(update_fields=['status', 'start_time', 'updated_at'])

    async def run_information_gathering():
        """Async function to run the information gathering with PydanticAI agents."""
        try:
            # Create the information gathering agent
            agent = create_information_gathering_service()

            logger.info(f"Extracting community info for Shop ID: {
                        shop_id}, Target: {target.name}")

            # Initial extraction using agent method
            initial_result = await agent.extract_community_info(target.website)
            logger.info(f"Completed initial extraction for Shop ID: {shop_id}")

            # Follow-up extraction for completeness using agent method
            final_result = await agent.gather_additional_info(target.website, initial_result)
            logger.info(
                f"Completed follow-up extraction for Shop ID: {shop_id}")

            return final_result

        except Exception as e:
            logger.error(f"Error in async information gathering for Shop ID {
                         shop_id}: {str(e)}")
            raise

    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            community_data = loop.run_until_complete(
                run_information_gathering())
        finally:
            loop.close()

        # Use a transaction to ensure atomicity when creating related objects
        with transaction.atomic():
            # Create or get the ShopResult linked to the Shop
            shop_result, created = ShopResult.objects.get_or_create(shop=shop)
            if created:
                logger.info(f"Created new ShopResult for Shop ID {shop_id}")
            else:
                logger.info(f"Found existing ShopResult for Shop ID {shop_id}")

            logger.info(f"Parsing and saving community info for ShopResult {
                        shop_result.shop_id}")
            _parse_and_save_community_info(shop_result, community_data)

        # Update shop status to COMPLETED
        shop.status = Shop.Status.COMPLETED
        shop.end_time = timezone.now()
        shop.save(update_fields=['status', 'end_time', 'updated_at'])
        logger.info(
            f"Successfully completed information gathering for Shop ID: {shop_id}")

    except Exception as e:
        logger.exception(
            f"Error during information gathering task for Shop ID {shop_id}: {e}")

        # Update shop status to ERROR
        try:
            shop.status = Shop.Status.ERROR
            shop.end_time = timezone.now()
            shop.save(update_fields=['status', 'end_time', 'updated_at'])
        except Exception as save_err:
            logger.error(f"Failed to update shop status to ERROR for Shop ID {
                         shop_id}: {save_err}")

        # Retry logic for Celery task
        try:
            # Exponential backoff retry delay
            retry_delay = RETRY_CONFIG['retry_delay'] * \
                (RETRY_CONFIG['backoff_factor'] ** self.request.retries)
            logger.warning(f"Retrying task for Shop ID {shop_id} (Attempt {
                           self.request.retries + 1}/{self.max_retries}) in {retry_delay}s...")
            raise self.retry(exc=e, countdown=retry_delay)
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for information gathering task for Shop ID {shop_id}.")
            # Final failure state is already set above
