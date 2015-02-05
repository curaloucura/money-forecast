# -*- coding: utf-8 -*- 
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import pytz

CURRENCY_CHOICES = (
    ('$','$ Dollar'),
    ('€','€ Euro'),
    ('R$','R$ Real'),
    ('£','£ Pound'),
    ('US$','US$ Dollar'),
)

TIMEZONE_CHOICES =[(x, x) for x in pytz.common_timezones]

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='$')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default=settings.TIME_ZONE)

@receiver(post_save, sender=User)
def generate_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)