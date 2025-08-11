import logging
import asyncio

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import (
    Shop,
    ShopResult,
    CommunityInfo,
    CommunityPage,
    FloorPlan,
    Amenity,
    Fee,
)
from apps.targets.models import Target
from utils.ai_integration.agents import MasterOrchestratorAgent
from utils.ai_integration.schemas import CommunityInformation
from utils.ai_integration.agent_config import RETRY_CONFIG

logger = logging.getLogger(__name__)


def _merge_fees(community_info: CommunityInfo, new_fees_data: list) -> None:
    """Merge new fees with existing ones, avoiding duplicates."""
    for fee_data in new_fees_data:
        # Use name and category as merge key
        merge_key = {
            "name__iexact": fee_data.fee_name.strip(),
            "fee_category__iexact": (fee_data.fee_category or "").strip(),
        }

        existing_fee = community_info.fees.filter(**merge_key).first()
        if existing_fee:
            # Update existing fee if new data is more complete
            updated = False
            if fee_data.amount and not existing_fee.amount:
                existing_fee.amount = fee_data.amount
                updated = True
            if fee_data.description and not existing_fee.description:
                existing_fee.description = fee_data.description
                updated = True
            if fee_data.source_url and not existing_fee.source_url:
                existing_fee.source_url = fee_data.source_url
                updated = True
            if fee_data.conditions and not existing_fee.conditions:
                existing_fee.conditions = fee_data.conditions
                updated = True

            if updated:
                existing_fee.save()
                logger.info(f"Updated existing fee: {existing_fee.name}")
            else:
                logger.info(f"Skipped duplicate fee: {fee_data.fee_name}")
        else:
            # Create new fee
            Fee.objects.create(
                community_info=community_info,
                name=fee_data.fee_name,
                amount=fee_data.amount,
                description=fee_data.description,
                refundable=fee_data.refundable,
                frequency=(
                    fee_data.frequency.upper()
                    if fee_data.frequency
                    else Fee.Frequency.ONE_TIME
                ),
                fee_category=fee_data.fee_category,
                source_url=fee_data.source_url,
                conditions=fee_data.conditions or "",
            )
            logger.info(
                f"Added new fee: {fee_data.fee_name} - ${fee_data.amount} - "
                f"Category: {fee_data.fee_category}, Refundable: {fee_data.refundable}"
            )


def _merge_floor_plans(
    community_info: CommunityInfo, new_floor_plans_data: list
) -> None:
    """Merge new floor plans with existing ones, avoiding duplicates and preserving unique data."""
    for fp_data in new_floor_plans_data:
        # Use name, beds, and baths as merge key
        merge_key = {
            "name__iexact": fp_data.name.strip(),
            "beds": fp_data.beds,
            "baths": fp_data.baths,
        }

        existing_floor_plan = community_info.floor_plans.filter(**merge_key).first()

        if existing_floor_plan:
            # Update existing floor plan if new data is more complete
            updated = False
            if fp_data.min_rental_price and not existing_floor_plan.min_rental_price:
                existing_floor_plan.min_rental_price = fp_data.min_rental_price
                updated = True
            if fp_data.max_rental_price and not existing_floor_plan.max_rental_price:
                existing_floor_plan.max_rental_price = fp_data.max_rental_price
                updated = True
            if fp_data.security_deposit and not existing_floor_plan.security_deposit:
                existing_floor_plan.security_deposit = fp_data.security_deposit
                updated = True
            if fp_data.sqft and not existing_floor_plan.sqft:
                existing_floor_plan.sqft = fp_data.sqft
                updated = True
            if fp_data.url and not existing_floor_plan.url:
                existing_floor_plan.url = fp_data.url
                updated = True
            if fp_data.type and not existing_floor_plan.type:
                existing_floor_plan.type = fp_data.type
                updated = True
            if getattr(fp_data, 'image', None) and not existing_floor_plan.image:
                existing_floor_plan.image = fp_data.image
                updated = True
            if getattr(fp_data, 'num_available', None) and not existing_floor_plan.num_available:
                existing_floor_plan.num_available = fp_data.num_available
                updated = True

            if updated:
                existing_floor_plan.save()
                logger.info(f"Updated existing floor plan: {existing_floor_plan.name}")

            # Merge amenities for this floor plan
            for amenity_data in fp_data.floor_plan_amenities:
                if amenity_data.amenity:
                    amenity, _ = Amenity.objects.get_or_create(
                        name=amenity_data.amenity
                    )
                    if not existing_floor_plan.amenities.filter(id=amenity.id).exists():
                        existing_floor_plan.amenities.add(amenity)
                        logger.info(
                            f"Added amenity '{amenity.name}' to existing floor plan '{existing_floor_plan.name}'"
                        )

            logger.info(f"Preserved existing floor plan: {fp_data.name}")
        else:
            # Create new floor plan
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
                image=getattr(fp_data, 'image', None),
                num_available=getattr(fp_data, 'num_available', None),
            )

            # Handle floor plan amenities
            for amenity_data in fp_data.floor_plan_amenities:
                if amenity_data.amenity:
                    amenity, _ = Amenity.objects.get_or_create(
                        name=amenity_data.amenity
                    )
                    floor_plan.amenities.add(amenity)

            logger.info(
                f"Added new floor plan: {fp_data.name} - "
                f"Beds: {fp_data.beds}, Baths: {fp_data.baths}, "
                f"Min Price: {fp_data.min_rental_price}, "
                f"Max Price: {fp_data.max_rental_price}"
            )


def _merge_community_pages(community_info: CommunityInfo, new_pages_data: list) -> None:
    """Merge new community pages with existing ones, avoiding duplicates."""
    for page_data in new_pages_data:
        # Use URL as primary merge key, fallback to name
        existing_page = None
        if page_data.url:
            existing_page = community_info.pages.filter(
                url__iexact=page_data.url.strip()
            ).first()

        if not existing_page and page_data.name:
            existing_page = community_info.pages.filter(
                name__iexact=page_data.name.strip()
            ).first()

        if existing_page:
            # Update existing page if new data is more complete
            updated = False
            if page_data.overview and not existing_page.overview:
                existing_page.overview = page_data.overview
                updated = True
            if page_data.url and not existing_page.url:
                existing_page.url = page_data.url
                updated = True

            if updated:
                existing_page.save()
                logger.info(f"Updated existing community page: {existing_page.name}")
            else:
                logger.info(f"Preserved existing community page: {page_data.name}")
        else:
            # Create new page
            CommunityPage.objects.create(
                community_info=community_info,
                name=page_data.name,
                overview=page_data.overview,
                url=page_data.url,
            )
            logger.info(f"Added new community page: {page_data.name}")


def _merge_community_amenities(
    community_info: CommunityInfo, new_amenities_data: list
) -> None:
    """Merge new community amenities with existing ones, avoiding duplicates."""
    for amenity_data in new_amenities_data:
        if amenity_data.amenity:
            amenity, created = Amenity.objects.get_or_create(
                name__iexact=amenity_data.amenity.strip(),
                defaults={"name": amenity_data.amenity.strip()},
            )

            if not community_info.community_amenities.filter(id=amenity.id).exists():
                community_info.community_amenities.add(amenity)
                logger.info(f"Added new community amenity: {amenity.name}")
            else:
                logger.info(f"Preserved existing community amenity: {amenity.name}")


def _parse_and_save_community_info(
    shop_result: ShopResult, community_info_data: CommunityInformation
) -> None:
    """
    Parses the PydanticAI response data and merges it with existing CommunityInfo data,
    preserving unique information from previous extractions.

    Args:
        shop_result: The ShopResult instance to associate the data with
        community_info_data: The CommunityInformation Pydantic model instance
    """
    # Create or update CommunityInfo
    logger.info(
        f"Merging community info with {len(community_info_data.fees)} new fees, "
        f"{len(community_info_data.floor_plans)} new floor plans"
    )

    community_info, created = CommunityInfo.objects.update_or_create(
        shop_result=shop_result,
        defaults={
            "name": community_info_data.name,
            "overview": community_info_data.overview,
            "url": community_info_data.url,
            "pet_policy": community_info_data.pet_policy,
            "pet_policy_source": community_info_data.pet_policy_source,
            "self_showings": community_info_data.self_showings,
            "self_showings_source": community_info_data.self_showings_source,
            "office_hours": community_info_data.office_hours,
            "resident_portal_provider": community_info_data.resident_portal_software_provider,
            "street_address": community_info_data.street_address,
            "city": community_info_data.city,
            "state": community_info_data.state,
            "zip_code": community_info_data.zip_code,
            "special_offers": community_info_data.special_offers,
        },
    )

    action = "Created" if created else "Updated"
    logger.info(
        f"{action} CommunityInfo {community_info.id} for ShopResult {shop_result.shop_id}"
    )

    # If this is a new community info, we don't need to merge, just create
    if created:
        logger.info("New CommunityInfo - creating all data without merge logic")

        # Create Fee objects
        for fee_data in community_info_data.fees:
            Fee.objects.create(
                community_info=community_info,
                name=fee_data.fee_name,
                amount=fee_data.amount,
                description=fee_data.description,
                refundable=fee_data.refundable,
                frequency=(
                    fee_data.frequency.upper()
                    if fee_data.frequency
                    else Fee.Frequency.ONE_TIME
                ),
                fee_category=fee_data.fee_category,
                source_url=fee_data.source_url,
                conditions=fee_data.conditions or "",
            )
            logger.info(f"Created fee: {fee_data.fee_name}")

        # Create CommunityPage objects
        for page_data in community_info_data.community_pages:
            CommunityPage.objects.create(
                community_info=community_info,
                name=page_data.name,
                overview=page_data.overview,
                url=page_data.url,
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
                image=getattr(fp_data, 'image', None),
                num_available=getattr(fp_data, 'num_available', None),
            )
            logger.info(f"Created floor plan: {floor_plan.name}")

            # Handle floor plan amenities
            for amenity_data in fp_data.floor_plan_amenities:
                if amenity_data.amenity:
                    amenity, _ = Amenity.objects.get_or_create(
                        name=amenity_data.amenity
                    )
                    floor_plan.amenities.add(amenity)

        # Handle community amenities
        for amenity_data in community_info_data.community_amenities:
            if amenity_data.amenity:
                amenity, _ = Amenity.objects.get_or_create(name=amenity_data.amenity)
                community_info.community_amenities.add(amenity)
    else:
        # Existing community info - use intelligent merging
        logger.info(
            "Existing CommunityInfo - using intelligent merge logic to preserve data"
        )

        # Count existing data before merge
        existing_fees_count = community_info.fees.count()
        existing_floor_plans_count = community_info.floor_plans.count()
        existing_pages_count = community_info.pages.count()
        existing_amenities_count = community_info.community_amenities.count()

        logger.info(
            f"Before merge - Fees: {existing_fees_count}, Floor Plans: {existing_floor_plans_count}, "
            f"Pages: {existing_pages_count}, Amenities: {existing_amenities_count}"
        )

        # Merge data using intelligent logic
        _merge_fees(community_info, community_info_data.fees)
        _merge_floor_plans(community_info, community_info_data.floor_plans)
        _merge_community_pages(community_info, community_info_data.community_pages)
        _merge_community_amenities(
            community_info, community_info_data.community_amenities
        )

        # Count final data after merge
        final_fees_count = community_info.fees.count()
        final_floor_plans_count = community_info.floor_plans.count()
        final_pages_count = community_info.pages.count()
        final_amenities_count = community_info.community_amenities.count()

        logger.info(
            f"After merge - Fees: {final_fees_count} (+{final_fees_count - existing_fees_count}), "
            f"Floor Plans: {final_floor_plans_count} (+{final_floor_plans_count - existing_floor_plans_count}), "
            f"Pages: {final_pages_count} (+{final_pages_count - existing_pages_count}), "
            f"Amenities: {final_amenities_count} (+{final_amenities_count - existing_amenities_count})"
        )


@shared_task(bind=True, max_retries=RETRY_CONFIG["max_retries"])
def start_information_gathering_task(self, shop_id: str) -> None:
    """
    Celery task to perform AI-driven information gathering for a given Shop using PydanticAI.
    """
    logger.info(f"Starting information gathering task for Shop ID: {shop_id}")

    try:
        shop = Shop.objects.select_related("target").get(id=shop_id)
        target = shop.target
    except Shop.DoesNotExist:
        logger.error(f"Shop with ID {shop_id} not found. Aborting task.")
        return
    except Target.DoesNotExist:
        logger.error(
            f"Target associated with Shop ID {
                     shop_id} not found. Aborting task."
        )
        shop.status = Shop.Status.ERROR
        shop.end_time = timezone.now()
        shop.save(update_fields=["status", "end_time", "updated_at"])
        return

    # Update shop status to IN_PROGRESS
    shop.status = Shop.Status.IN_PROGRESS
    shop.start_time = timezone.now()
    shop.save(update_fields=["status", "start_time", "updated_at"])

    async def run_information_gathering():
        """Async function to run the multi-agent information gathering with orchestrator."""
        try:
            # Create the master orchestrator agent
            orchestrator = MasterOrchestratorAgent()

            logger.info(
                f"Starting multi-agent orchestrated extraction for Shop ID: {
                        shop_id}, Target: {target.name}"
            )

            # Prepare target data for validation context
            target_data = {
                'name': target.name,
                'street_address': target.street_address,
                'city': target.city,
                'state': target.state,
                'zip_code': target.zip_code,
                'phone_number': target.phone_number,
                'email_address': target.email_address,
                'website': target.website,
                'property_manager': target.property_manager
            }
            
            # Run orchestrated extraction with specialized agents
            orchestration_result = await orchestrator.orchestrate_extraction(
                target.website, target_data=target_data
            )
            logger.info(f"Completed orchestrated extraction for Shop ID: {shop_id}")
            logger.info(
                f"Orchestration summary: {orchestration_result.extraction_summary}"
            )
            logger.info(
                f"Final validation score: {orchestration_result.final_validation_score}%"
            )
            logger.info(
                f"Quality assessment: {orchestration_result.quality_assessment}"
            )

            return orchestration_result.final_community_info

        except Exception as e:
            logger.error(
                f"Error in async multi-agent information gathering for Shop ID {
                         shop_id}: {str(e)}"
            )
            raise

    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            community_data = loop.run_until_complete(run_information_gathering())
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

            logger.info(
                f"Parsing and saving community info for ShopResult {
                        shop_result.shop_id}"
            )
            logger.info(
                f"Community data contains {len(community_data.floor_plans)} floor plans"
            )
            for i, fp in enumerate(community_data.floor_plans):
                logger.info(f"Floor plan {i+1}: {fp.name}")
            _parse_and_save_community_info(shop_result, community_data)

        # Update shop status to COMPLETED
        shop.status = Shop.Status.COMPLETED
        shop.end_time = timezone.now()
        shop.save(update_fields=["status", "end_time", "updated_at"])
        logger.info(
            f"Successfully completed information gathering for Shop ID: {shop_id}"
        )

    except Exception as e:
        logger.exception(
            f"Error during information gathering task for Shop ID {shop_id}: {e}"
        )

        # Update shop status to ERROR
        try:
            shop.status = Shop.Status.ERROR
            shop.end_time = timezone.now()
            shop.save(update_fields=["status", "end_time", "updated_at"])
        except Exception as save_err:
            logger.error(
                f"Failed to update shop status to ERROR for Shop ID {
                         shop_id}: {save_err}"
            )

        # Retry logic for Celery task
        try:
            # Exponential backoff retry delay
            retry_delay = RETRY_CONFIG["retry_delay"] * (
                RETRY_CONFIG["backoff_factor"] ** self.request.retries
            )
            logger.warning(
                f"Retrying task for Shop ID {shop_id} (Attempt {
                           self.request.retries + 1}/{self.max_retries}) in {retry_delay}s..."
            )
            raise self.retry(exc=e, countdown=retry_delay)
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for information gathering task for Shop ID {shop_id}."
            )
            # Final failure state is already set above
