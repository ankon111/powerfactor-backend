# Generated by Django 4.1.2 on 2022-10-27 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Datapoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('energy_expected', models.FloatField()),
                ('energy_observed', models.FloatField()),
                ('irradiation_expected', models.FloatField()),
                ('irradiation_observed', models.FloatField()),
                ('plant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datapoint',
                                            to='solar_plant_app.plant')),
            ],
            options={
                'unique_together': {('plant', 'timestamp')},
            },
        ),
    ]
