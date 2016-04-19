# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BetaTestApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('subdomain', models.CharField(verbose_name='domain name', unique=True, max_length=255, help_text='The URL students will visit. In the future, you will also have the possibility to use your own domain name.\n\nExample: hogwarts.opencraft.hosting')),
                ('instance_name', models.CharField(help_text='The name of your institution, company or project.\n\nExample: Hogwarts Online Learning', max_length=255)),
                ('public_contact_email', models.EmailField(help_text='The email your instance of Open edX will be using to send emails, and where your users should send their support requests.\n\nThis needs to be a valid email.', max_length=254)),
                ('project_description', models.TextField(verbose_name='your project', help_text='What are you going to use the instance for? What are your expectations?')),
                ('subscribe_to_updates', models.BooleanField(help_text='I want OpenCraft to keep me updated about the progress of the beta test, and send me an email occasionally about it.', default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], max_length=255, default='pending')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
