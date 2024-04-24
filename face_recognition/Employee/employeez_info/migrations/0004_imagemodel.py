# Generated by Django 4.2.7 on 2024-04-07 22:36

from django.db import migrations, models
import employeez_info.models


class Migration(migrations.Migration):

    dependencies = [
        ('employeez_info', '0003_alter_employee_info_email_alter_employee_info_nid_no_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marked_time', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(upload_to=employeez_info.models.get_upload_path)),
            ],
        ),
    ]