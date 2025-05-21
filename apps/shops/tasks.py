import logging
import json
from typing import Dict, Any

from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import Shop, ShopResult, CommunityInfo, CommunityPage, FloorPlan, Amenity
from apps.targets.models import Target
from utils.ai_integration.openai_client import OpenAIClient
from utils.ai_integration.prompt_templates import PromptTemplates
from utils.ai_integration.ai_config import (
    get_api_key,
    get_model_config,
    API_RETRY_CONFIG
)

logger = logging.getLogger(__name__)


def _parse_and_save_community_info(shop_result: ShopResult, ai_response_data: Dict[str, Any]) -> None:
    """
    Parses the AI response data and saves it to the CommunityInfo related models.
    This is a complex function and needs careful implementation based on the exact
    structure of ai_response_data matching the 'properties' section of STRUCTURED_OUTPUT_INFORMATION_GATHERING.
    """
    # Expecting ai_response_data to be the dictionary containing community properties
    if not isinstance(ai_response_data, dict):
        logger.error(f"Invalid data type passed to _parse_and_save_community_info for ShopResult {
                     shop_result.shop_id}. Expected dict, got {type(ai_response_data)}.")
        raise TypeError("Invalid data type for parsing community info.")

    community_data = ai_response_data  # Use the passed dictionary directly

    # Create or update CommunityInfo
    # Using update_or_create to handle potential retries or re-runs
    community_info, created = CommunityInfo.objects.update_or_create(
        shop_result=shop_result,
        defaults={
            'name': community_data.get('name'),
            'overview': community_data.get('overview'),
            'url': community_data.get('url'),
            'application_fee': community_data.get('application_fee'),
            'application_fee_source': community_data.get('application_fee_source'),
            'administration_fee': community_data.get('administration_fee'),
            'administration_fee_source': community_data.get('administration_fee_source'),
            'membership_fee': community_data.get('membership_fee'),
            'membership_fee_source': community_data.get('membership_fee_source'),
            'pet_policy': community_data.get('pet_policy'),
            'pet_policy_source': community_data.get('pet_policy_source'),
            'self_showings': community_data.get('self_showings'),
            'self_showings_source': community_data.get('self_showings_source'),
            'office_hours': community_data.get('office_hours'),
            # Corrected key
            'resident_portal_provider': community_data.get('resident_portal_software_provider'),
            # Note: amenities are handled separately below
        }
    )
    logger.info(f"{'Created' if created else 'Updated'} CommunityInfo {
                community_info.id} for ShopResult {shop_result.shop_id}")

    # Clear existing related objects before adding new ones to prevent duplicates on update
    community_info.pages.all().delete()
    community_info.floor_plans.all().delete()
    community_info.community_amenities.clear()  # ManyToMany field

    # Create CommunityPage objects
    for page_data in community_data.get('community_pages', []):
        CommunityPage.objects.create(
            community_info=community_info,
            name=page_data.get('name'),
            overview=page_data.get('overview'),
            url=page_data.get('url')
        )

    # Create FloorPlan objects and their amenities
    for fp_data in community_data.get('floor_plans', []):
        floor_plan = FloorPlan.objects.create(
            community_info=community_info,
            name=fp_data.get('name'),
            beds=fp_data.get('beds'),
            baths=fp_data.get('baths'),
            url=fp_data.get('url'),
            sqft=fp_data.get('sqft'),
            type=fp_data.get('type'),
            min_rental_price=fp_data.get('min_rental_price'),
            max_rental_price=fp_data.get('max_rental_price'),
            security_deposit=fp_data.get('security_deposit'),
        )
        # Handle floor plan amenities (assuming they are strings for now)
        for amenity_data in fp_data.get('floor_plan_amenities', []):
            amenity_name = amenity_data.get('amenity')
            if amenity_name:
                amenity, _ = Amenity.objects.get_or_create(name=amenity_name)
                floor_plan.amenities.add(amenity)  # Add to ManyToManyField

    # Handle community amenities
    for amenity_data in community_data.get('community_amenities', []):
        amenity_name = amenity_data.get('amenity')
        if amenity_name:
            amenity, _ = Amenity.objects.get_or_create(name=amenity_name)
            community_info.community_amenities.add(
                amenity)  # Add to ManyToManyField


@shared_task(bind=True, max_retries=API_RETRY_CONFIG['max_retries'])
def start_information_gathering_task(self, shop_id: str) -> None:
    """
    Celery task to perform AI-driven information gathering for a given Shop.
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
        # Optionally update shop status to FAILED here
        shop.status = Shop.Status.ERROR
        shop.end_time = timezone.now()
        shop.save(update_fields=['status', 'end_time', 'updated_at'])
        return

    # Update shop status to IN_PROGRESS
    shop.status = Shop.Status.IN_PROGRESS
    shop.start_time = timezone.now()
    shop.save(update_fields=['status', 'start_time', 'updated_at'])

    try:
        # --- AI Interaction ---
        logger.info("Fetching AI configuration for information gathering.")
        ai_config = get_model_config('information_gathering')
        api_key = get_api_key(ai_config.get('service', 'openai'))

        if not api_key:
            raise ValueError(f"API key for service '{
                             ai_config.get('service')}' not found.")

        # Assuming OpenAI for now, adjust if multiple services are supported
        if ai_config.get('service') == 'openai':
            client = OpenAIClient(api_key=api_key)

            logger.info(f"Sending request to AI for Shop ID: {
                        shop_id}, Target: {target.name}")

            # Generate the prompt using the PromptTemplates class
            prompt = PromptTemplates.information_gathering()
            user_input = target.website

            model_input = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_input
                        }
                    ]
                }
            ]

            initial_ai_response_str = client.generate_response(
                input=model_input,
                model=ai_config.get('model'),
                temperature=ai_config.get('temperature'),
                max_output_tokens=ai_config.get('max_output_tokens'),
                tools=ai_config.get('tools'),
                tool_choice=ai_config.get('tool_choice'),
                text=ai_config.get('text')
            )

            update_prompt = PromptTemplates.information_gathering_follow_up()

            model_input.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": initial_ai_response_str
                    }
                ]
            })

            model_input.append({
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": update_prompt
                    }
                ]
            })

            ai_response_str = client.generate_response(
                input=model_input,
                model=ai_config.get('model'),
                temperature=ai_config.get('temperature'),
                max_output_tokens=ai_config.get('max_output_tokens'),
                tools=ai_config.get('tools'),
                tool_choice=ai_config.get('tool_choice'),
                text=ai_config.get('text')
            )

            # --- Response Parsing and Saving ---
            logger.info(f"Received AI response for Shop ID: {
                        shop_id}. Parsing...")

            try:
                # Attempt to parse the raw string response as JSON
                parsed_json = json.loads(ai_response_str)

                # Check if the parsed result is itself a string (double-encoded JSON)
                if isinstance(parsed_json, str):
                    logger.warning(f"AI response for Shop ID {
                                   shop_id} appears double-encoded. Attempting second parse.")
                    parsed_json = json.loads(parsed_json)

                # Now, parsed_json should be the dictionary matching the schema's properties
                if not isinstance(parsed_json, dict):
                    logger.error(f"Parsed AI response for Shop ID {
                                 shop_id} is not a dictionary. Type: {type(parsed_json)}")
                    raise ValueError("Parsed AI response is not a dictionary.")

                response_data = parsed_json  # This is the dictionary we need

            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to decode JSON response for Shop ID {
                             shop_id}: {json_err}")
                logger.error(f"Raw AI Response: {ai_response_str}")
                raise ValueError(f"Invalid JSON received from AI: {
                                 json_err}") from json_err
            except Exception as parse_err:  # Catch other potential errors during parsing/checking
                logger.error(f"Error processing AI response structure for Shop ID {
                             shop_id}: {parse_err}")
                logger.error(f"Raw AI Response: {ai_response_str}")
                raise ValueError(f"Unexpected AI response structure or content: {
                                 parse_err}") from parse_err

            # Use a transaction to ensure atomicity when creating related objects
            with transaction.atomic():
                # Create or get the ShopResult linked to the Shop
                shop_result, created = ShopResult.objects.get_or_create(
                    shop=shop)
                if created:
                    logger.info(
                        f"Created new ShopResult for Shop ID {shop_id}")
                else:
                    logger.info(
                        f"Found existing ShopResult for Shop ID {shop_id}")

                logger.info(f"Parsing and saving community info for ShopResult {
                            shop_result.shop_id}")  # Use shop_result.shop_id
                # Pass the extracted dictionary
                _parse_and_save_community_info(shop_result, response_data)

            # Update shop status to COMPLETED
            shop.status = Shop.Status.COMPLETED
            shop.end_time = timezone.now()
            shop.save(update_fields=['status', 'end_time', 'updated_at'])
            logger.info(
                f"Successfully completed information gathering for Shop ID: {shop_id}")

        else:
            # Handle other potential AI services if needed
            logger.error(f"Unsupported AI service configured: {
                         ai_config.get('service')}")
            raise NotImplementedError(
                f"AI service '{ai_config.get('service')}' not implemented.")

    except Exception as e:
        logger.exception(
            f"Error during information gathering task for Shop ID {shop_id}: {e}")
        # Update shop status to FAILED
        try:
            shop.status = Shop.Status.ERROR
            shop.end_time = timezone.now()
            shop.save(update_fields=['status', 'end_time', 'updated_at'])
        except Exception as save_err:
            logger.error(f"Additionally failed to update shop status to FAILED for Shop ID {
                         shop_id}: {save_err}")

        # Retry logic for Celery task based on the exception
        try:
            # Default retry delay from config, exponential backoff
            retry_delay = API_RETRY_CONFIG['retry_delay'] * \
                (API_RETRY_CONFIG['backoff_factor'] ** self.request.retries)
            logger.warning(f"Retrying task for Shop ID {shop_id} (Attempt {
                           self.request.retries + 1}/{self.max_retries}) in {retry_delay}s...")
            raise self.retry(exc=e, countdown=retry_delay)
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for information gathering task for Shop ID {shop_id}.")
            # Final failure state is already set above
