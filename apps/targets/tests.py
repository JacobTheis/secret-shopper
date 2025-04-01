from django.test import TestCase
from .models import Target


class TargetModelTests(TestCase):
    """Tests for the Target model."""

    def test_create_target(self):
        """Test creating a Target instance."""
        target = Target.objects.create(
            name="Test Property",
            street_address="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="90210",
            phone_number="555-1234",
            email_address="test@example.com",
            website="http://example.com",
            owners="Test Owner Inc.",
            property_manager="John Doe",
        )
        self.assertEqual(target.name, "Test Property")
        self.assertEqual(target.city, "Anytown")
        self.assertEqual(str(target), "Test Property")
        self.assertIsNotNone(target.id)
        self.assertIsNotNone(target.created_at)
        self.assertIsNotNone(target.updated_at)

    def test_target_str_method(self):
        """Test the __str__ method of the Target model."""
        target = Target(name="Another Property")
        self.assertEqual(str(target), "Another Property")
