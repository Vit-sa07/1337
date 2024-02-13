from django.contrib.auth.models import User
import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.BigIntegerField('Telegram ID', unique=True, null=True, blank=True)
    phone_number = models.CharField('Номер телефона', max_length=20, unique=True)
    full_name = models.CharField('ФИО', max_length=255)
    city = models.CharField('Город', max_length=100)
    age = models.PositiveIntegerField('Возраст', null=True, blank=True)
    referral_code = models.UUIDField(unique=True, null=True, editable=False, blank=True)
    discount = models.IntegerField(default=0)
    is_verified = models.BooleanField('Подтверждён', default=False)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4()
        super(UserProfile, self).save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        instance.profile.save()
