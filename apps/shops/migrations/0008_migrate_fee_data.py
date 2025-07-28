# Generated migration to migrate fee data from CommunityInfo fields to Fee model

from django.db import migrations, models
import django.db.models.deletion
import re


def migrate_fee_data_forward(apps, schema_editor):
    """Move fee data from CommunityInfo fields to Fee model."""
    CommunityInfo = apps.get_model('shops', 'CommunityInfo')
    Fee = apps.get_model('shops', 'Fee')
    
    print("Starting fee data migration...")
    
    for community_info in CommunityInfo.objects.all():
        fees_created = 0
        
        # Migrate application fee
        if community_info.application_fee is not None:
            Fee.objects.create(
                community_info=community_info,
                name="Application Fee",
                amount=community_info.application_fee,
                description="Fee charged for applying to live in the community",
                refundable=False,
                frequency="ONE_TIME",
                fee_category="Application",
                source_url=community_info.application_fee_source or "",
                conditions="",
            )
            fees_created += 1
            print(f"  Created application fee: ${community_info.application_fee}")
        
        # Migrate administration fee
        if community_info.administration_fee is not None:
            Fee.objects.create(
                community_info=community_info,
                name="Administration Fee",
                amount=community_info.administration_fee,
                description="One-time administrative fee",
                refundable=False,
                frequency="ONE_TIME",
                fee_category="Administrative",
                source_url=community_info.administration_fee_source or "",
                conditions="",
            )
            fees_created += 1
            print(f"  Created administration fee: ${community_info.administration_fee}")
        
        # Migrate membership fee (more complex as it can be text)
        if community_info.membership_fee:
            # Try to extract dollar amount from membership fee string
            amount = None
            membership_text = str(community_info.membership_fee)
            
            # Look for dollar amounts in the text
            dollar_match = re.search(r'\$(\d+(?:\.\d{2})?)', membership_text)
            if dollar_match:
                try:
                    amount = float(dollar_match.group(1))
                except ValueError:
                    amount = None
            
            Fee.objects.create(
                community_info=community_info,
                name="Membership Fee",
                amount=amount,
                description=membership_text,
                refundable=False,
                frequency="MONTHLY" if "month" in membership_text.lower() else "ONE_TIME",
                fee_category="Membership",
                source_url=community_info.membership_fee_source or "",
                conditions="",
            )
            fees_created += 1
            print(f"  Created membership fee: {membership_text} (amount: ${amount})")
        
        if fees_created > 0:
            print(f"Migrated {fees_created} fees for community: {community_info.name}")


def migrate_fee_data_reverse(apps, schema_editor):
    """Reverse migration - move Fee data back to CommunityInfo fields."""
    CommunityInfo = apps.get_model('shops', 'CommunityInfo')
    Fee = apps.get_model('shops', 'Fee')
    
    print("Reversing fee data migration...")
    
    for community_info in CommunityInfo.objects.all():
        fees = Fee.objects.filter(community_info=community_info)
        
        for fee in fees:
            # Map fees back to the original fields based on category
            if fee.fee_category.lower() == 'application':
                community_info.application_fee = fee.amount
                community_info.application_fee_source = fee.source_url
            elif fee.fee_category.lower() in ['administrative', 'administration']:
                community_info.administration_fee = fee.amount
                community_info.administration_fee_source = fee.source_url
            elif fee.fee_category.lower() == 'membership':
                if fee.amount:
                    community_info.membership_fee = f"${fee.amount}"
                else:
                    community_info.membership_fee = fee.description
                community_info.membership_fee_source = fee.source_url
        
        community_info.save()
        print(f"Restored fee data for community: {community_info.name}")


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_fix_resident_portal_provider_nullable'),
    ]

    operations = [
        # First create the Fee model (copy from the generated migration)
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="The name or title of the fee (e.g., 'Application Fee', 'Pet Deposit').", max_length=255)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, help_text='The fee amount. Can be null if the fee has no specific amount.', max_digits=10, null=True)),
                ('description', models.TextField(blank=True, help_text='Detailed description of what the fee covers.')),
                ('refundable', models.BooleanField(default=False, help_text='Whether this fee is refundable.')),
                ('frequency', models.CharField(choices=[('ONE_TIME', 'One-time'), ('MONTHLY', 'Monthly'), ('ANNUAL', 'Annual'), ('CONDITIONAL', 'Conditional')], default='ONE_TIME', help_text='How often this fee is charged.', max_length=20)),
                ('fee_category', models.CharField(blank=True, help_text="Category of the fee (e.g., 'Application', 'Administrative', 'Pet').", max_length=100)),
                ('source_url', models.URLField(blank=True, help_text='The source URL where this fee information was found.', max_length=500, null=True)),
                ('conditions', models.TextField(blank=True, help_text='Any conditions or requirements for this fee.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community_info', models.ForeignKey(help_text='The community this fee belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='shops.communityinfo')),
            ],
            options={
                'verbose_name': 'Fee',
                'verbose_name_plural': 'Fees',
                'ordering': ['name'],
            },
        ),
        # Then migrate the data
        migrations.RunPython(
            migrate_fee_data_forward,
            migrate_fee_data_reverse,
        ),
    ]