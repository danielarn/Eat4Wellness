# Generated by Django 3.1.3 on 2020-11-09 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.member'),
        ),
    ]
