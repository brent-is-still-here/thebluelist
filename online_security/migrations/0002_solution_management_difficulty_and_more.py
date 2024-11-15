# Generated by Django 5.1.3 on 2024-11-12 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_security', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='management_difficulty',
            field=models.CharField(blank=True, choices=[('hands_off', 'Hands-Off'), ('low_maintenance', 'Low Maintenance'), ('steady_oversight', 'Steady Oversight'), ('high_touch', 'High Touch'), ('constant_vigilance', 'Constant Vigilance')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='solution',
            name='cost_duration',
            field=models.CharField(blank=True, choices=[('monthly', 'Monthly'), ('annual', 'Annual'), ('lifetime', 'Lifetime')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='solution',
            name='implementation_difficulty',
            field=models.CharField(blank=True, choices=[('plug_and_play', 'Plug-and-Play'), ('smooth_setup', 'Smooth Setup'), ('moderate_integration', 'Moderate Integration'), ('complex_configuration', 'Complex Configuration'), ('heavy_lifting', 'Heavy Lifting')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='solution',
            name='learning_curve',
            field=models.CharField(blank=True, choices=[('intuitive', 'Intuitive'), ('familiar_territory', 'Familiar Territory'), ('gradual_learning', 'Gradual Learning'), ('steep_climb', 'Steep Climb'), ('expert_only', 'Expert-Only')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='difficulty',
            field=models.CharField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('difficult', 'Difficult')], max_length=10),
        ),
    ]
