from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile, FacultyProfile

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'STUDENT':
            StudentProfile.objects.create(
                user=instance,
                department=None,  # You must handle this properly
                year=1,
                section='A'
            )
        elif instance.role == 'FACULTY':
            FacultyProfile.objects.create(
                user=instance,
                department=None,
                designation="Assistant Professor"
            )
