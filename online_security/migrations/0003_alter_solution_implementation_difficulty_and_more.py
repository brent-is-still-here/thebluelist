# Generated by Django 5.1.3 on 2024-11-12 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_security', '0002_solution_management_difficulty_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='implementation_difficulty',
            field=models.CharField(blank=True, choices=[('very_easy', 'Very Easy'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'), ('very_hard', 'Very Hard')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='solution',
            name='learning_curve',
            field=models.CharField(blank=True, choices=[('very_easy', 'Very Easy'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'), ('very_hard', 'Very Hard')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='solution',
            name='management_difficulty',
            field=models.CharField(blank=True, choices=[('very_easy', 'Very Easy'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'), ('very_hard', 'Very Hard')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='tutorial',
            name='difficulty',
            field=models.CharField(choices=[('very_easy', 'Very Easy'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard'), ('very_hard', 'Very Hard')], max_length=10),
        ),
    ]