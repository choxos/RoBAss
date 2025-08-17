# Generated migration for ROBINS-E support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0003_signallingquestion_explanation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domainassessment',
            name='bias_rating',
            field=models.CharField(blank=True, choices=[
                ('low', 'Low risk'), 
                ('some_concerns', 'Some concerns'), 
                ('high', 'High risk'), 
                ('very_high_risk', 'Very high risk'),
                ('no_information', 'No information')
            ], max_length=25),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='overall_bias',
            field=models.CharField(blank=True, max_length=75),  # Increased for longer ROBINS-E descriptions
        ),
    ]
