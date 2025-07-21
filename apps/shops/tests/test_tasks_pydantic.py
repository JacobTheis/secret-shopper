"""Tests for shops tasks using PydanticAI integration."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from django.utils import timezone

from apps.shops.models import Shop, ShopResult, CommunityInfo
from apps.targets.models import Target
from apps.shops.tasks import start_information_gathering_task, _parse_and_save_community_info
from utils.ai_integration.schemas import (
    CommunityInformation,
    FloorPlan,
    CommunityPage,
    FloorPlanAmenity,
    CommunityAmenity
)


class TestPydanticTaskIntegration(TestCase):
    """Test integration between Celery tasks and PydanticAI agents."""
    
    def setUp(self):
        """Set up test data."""
        self.target = Target.objects.create(
            name="Test Community",
            website="https://example.com"
        )
        self.shop = Shop.objects.create(
            target=self.target,
            status=Shop.Status.PENDING
        )
    
    def test_parse_and_save_community_info(self):
        """Test parsing and saving community info from Pydantic model."""
        # Create test data
        community_data = CommunityInformation(
            name="Luxury Apartments",
            overview="Premium community with modern amenities",
            url="https://example.com",
            application_fee=100.0,
            application_fee_source="https://example.com/fees",
            pet_policy="Pets allowed with deposit",
            self_showings=True,
            community_pages=[
                CommunityPage(
                    name="Amenities",
                    overview="Community amenities page",
                    url="https://example.com/amenities"
                )
            ],
            floor_plans=[
                FloorPlan(
                    name="1BR Deluxe",
                    beds=1,
                    baths=1,
                    url="https://example.com/1br",
                    type="apartment",
                    min_rental_price=1500.0,
                    max_rental_price=1800.0,
                    security_deposit=1000.0,
                    floor_plan_amenities=[
                        FloorPlanAmenity(amenity="Air Conditioning"),
                        FloorPlanAmenity(amenity="Dishwasher")
                    ]
                )
            ],
            community_amenities=[
                CommunityAmenity(amenity="Pool"),
                CommunityAmenity(amenity="Fitness Center")
            ]
        )
        
        # Create ShopResult
        shop_result = ShopResult.objects.create(shop=self.shop)
        
        # Run the function
        _parse_and_save_community_info(shop_result, community_data)
        
        # Verify CommunityInfo was created
        community_info = CommunityInfo.objects.get(shop_result=shop_result)
        assert community_info.name == "Luxury Apartments"
        assert community_info.overview == "Premium community with modern amenities"
        assert community_info.application_fee == 100.0
        assert community_info.pet_policy == "Pets allowed with deposit"
        assert community_info.self_showings is True
        
        # Verify related objects
        assert community_info.pages.count() == 1
        page = community_info.pages.first()
        assert page.name == "Amenities"
        
        assert community_info.floor_plans.count() == 1
        floor_plan = community_info.floor_plans.first()
        assert floor_plan.name == "1BR Deluxe"
        assert floor_plan.beds == 1
        assert floor_plan.min_rental_price == 1500.0
        assert floor_plan.amenities.count() == 2
        
        assert community_info.community_amenities.count() == 2
        amenity_names = [a.name for a in community_info.community_amenities.all()]
        assert "Pool" in amenity_names
        assert "Fitness Center" in amenity_names
    
    def test_parse_and_save_community_info_update(self):
        """Test that updating community info clears existing data."""
        # Create initial data
        shop_result = ShopResult.objects.create(shop=self.shop)
        community_info = CommunityInfo.objects.create(
            shop_result=shop_result,
            name="Old Name",
            overview="Old overview",
            url="https://old.com"
        )
        
        # Add some related data
        old_page = community_info.pages.create(
            name="Old Page",
            overview="Old page overview",
            url="https://old.com/page"
        )
        
        # Create new data to save
        new_community_data = CommunityInformation(
            name="New Community",
            overview="New overview",
            url="https://new.com",
            community_pages=[
                CommunityPage(
                    name="New Page",
                    overview="New page overview",
                    url="https://new.com/page"
                )
            ],
            floor_plans=[],
            community_amenities=[]
        )
        
        # Update the community info
        _parse_and_save_community_info(shop_result, new_community_data)
        
        # Verify the data was updated
        community_info.refresh_from_db()
        assert community_info.name == "New Community"
        assert community_info.overview == "New overview"
        
        # Verify old related data was cleared and new data added
        assert community_info.pages.count() == 1
        page = community_info.pages.first()
        assert page.name == "New Page"
        assert page.id != old_page.id  # Should be a new object
    
    @patch('apps.shops.tasks.create_information_gathering_service')
    @patch('asyncio.new_event_loop')
    def test_start_information_gathering_task_success(self, mock_new_loop, mock_create_service):
        """Test successful completion of information gathering task."""
        # Mock the async service
        mock_service = Mock()
        mock_community_data = CommunityInformation(
            name="Test Community",
            overview="Test overview",
            url="https://example.com",
            floor_plans=[],
            community_amenities=[],
            community_pages=[]
        )
        mock_service.run = AsyncMock(return_value=mock_community_data)
        mock_create_service.return_value = mock_service
        
        # Mock event loop
        mock_loop = Mock()
        mock_loop.run_until_complete.return_value = mock_community_data
        mock_new_loop.return_value = mock_loop
        
        # Create a mock task instance
        mock_task = Mock()
        mock_task.request.retries = 0
        mock_task.max_retries = 3
        
        # Run the task
        start_information_gathering_task(mock_task, str(self.shop.id))
        
        # Verify shop status was updated
        self.shop.refresh_from_db()
        assert self.shop.status == Shop.Status.COMPLETED
        assert self.shop.start_time is not None
        assert self.shop.end_time is not None
        
        # Verify ShopResult was created
        assert ShopResult.objects.filter(shop=self.shop).exists()
        shop_result = ShopResult.objects.get(shop=self.shop)
        
        # Verify CommunityInfo was created
        assert CommunityInfo.objects.filter(shop_result=shop_result).exists()
        community_info = CommunityInfo.objects.get(shop_result=shop_result)
        assert community_info.name == "Test Community"
        
        # Verify service was called twice (initial + followup)
        assert mock_service.run.call_count == 2
    
    @patch('apps.shops.tasks.create_information_gathering_service')
    @patch('asyncio.new_event_loop')
    def test_start_information_gathering_task_failure(self, mock_new_loop, mock_create_service):
        """Test handling of task failure."""
        # Mock service to raise an exception
        mock_service = Mock()
        mock_service.run = AsyncMock(side_effect=Exception("AI service failed"))
        mock_create_service.return_value = mock_service
        
        # Mock event loop
        mock_loop = Mock()
        mock_loop.run_until_complete.side_effect = Exception("AI service failed")
        mock_new_loop.return_value = mock_loop
        
        # Create a mock task instance that will retry
        mock_task = Mock()
        mock_task.request.retries = 0
        mock_task.max_retries = 3
        mock_task.retry.side_effect = mock_task.MaxRetriesExceededError()
        mock_task.MaxRetriesExceededError = type('MaxRetriesExceededError', (Exception,), {})
        
        # Run the task - should not raise exception but should update status
        start_information_gathering_task(mock_task, str(self.shop.id))
        
        # Verify shop status was set to error
        self.shop.refresh_from_db()
        assert self.shop.status == Shop.Status.ERROR
        assert self.shop.end_time is not None
        
        # Verify retry was attempted
        mock_task.retry.assert_called_once()
    
    def test_start_information_gathering_task_shop_not_found(self):
        """Test handling when shop is not found."""
        # Create a mock task instance
        mock_task = Mock()
        
        # Try to run task with non-existent shop ID
        start_information_gathering_task(mock_task, "999999")
        
        # Should complete without error (just logs and returns)
        # No assertions needed as the function should handle this gracefully
    
    def test_start_information_gathering_task_no_target(self):
        """Test handling when shop has no associated target."""
        # Create shop without target
        shop_without_target = Shop.objects.create(
            target=None,
            status=Shop.Status.PENDING
        )
        
        # Create a mock task instance
        mock_task = Mock()
        
        # Run the task
        start_information_gathering_task(mock_task, str(shop_without_target.id))
        
        # Verify shop status was set to error
        shop_without_target.refresh_from_db()
        assert shop_without_target.status == Shop.Status.ERROR
        assert shop_without_target.end_time is not None


class TestCommunityInfoSchemaMapping(TestCase):
    """Test mapping between Pydantic schemas and Django models."""
    
    def test_floor_plan_optional_fields(self):
        """Test floor plan with optional fields as None."""
        floor_plan_data = FloorPlan(
            name="Studio",
            beds=0,
            baths=1,
            url="https://example.com/studio",
            type="apartment",
            sqft=None,  # Optional field
            min_rental_price=None,  # Optional field
            max_rental_price=None,  # Optional field
            security_deposit=None,  # Optional field
            floor_plan_amenities=[]
        )
        
        # Should not raise any validation errors
        assert floor_plan_data.name == "Studio"
        assert floor_plan_data.sqft is None
        assert floor_plan_data.min_rental_price is None
    
    def test_community_info_with_empty_collections(self):
        """Test community info with empty collections."""
        community_data = CommunityInformation(
            name="Empty Community",
            overview="Community with no extra data",
            url="https://example.com",
            floor_plans=[],
            community_amenities=[],
            community_pages=[]
        )
        
        assert len(community_data.floor_plans) == 0
        assert len(community_data.community_amenities) == 0
        assert len(community_data.community_pages) == 0
    
    def test_amenity_schema_validation(self):
        """Test amenity schema validation."""
        floor_plan_amenity = FloorPlanAmenity(amenity="Air Conditioning")
        community_amenity = CommunityAmenity(amenity="Pool")
        
        assert floor_plan_amenity.amenity == "Air Conditioning"
        assert community_amenity.amenity == "Pool"
        
        # Test empty amenity name (should still be valid but empty)
        empty_amenity = FloorPlanAmenity(amenity="")
        assert empty_amenity.amenity == ""