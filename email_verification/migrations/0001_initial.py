# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('email', models.EmailField(serialize=False, primary_key=True, max_length=254)),
                ('verified', models.BooleanField(default=False)),
                ('verification_code', models.CharField(db_index=True, max_length=64)),
                ('verification_email_date', models.DateTimeField(null=True)),
                ('verification_date', models.DateTimeField(null=True)),
            ],
        ),
    ]
