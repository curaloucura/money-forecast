# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import pytz

CURRENCY_CHOICES = (
    ('d', '$'),
    ('eur', '€'),
    ('brl', 'R$'),
    ('bpd', '£'),
    ('usd', 'US$'),
)

TIMEZONE_CHOICES = [(x, x) for x in pytz.common_timezones]


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    currency = models.CharField(
        max_length=5, choices=CURRENCY_CHOICES, default='$')
    timezone = models.CharField(
        max_length=50, choices=TIMEZONE_CHOICES, default=settings.TIME_ZONE)

    def __unicode__(self):
        return self.user.get_full_name() or self.user.username


@receiver(post_save, sender=User)
def generate_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
