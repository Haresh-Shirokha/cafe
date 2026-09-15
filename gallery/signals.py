from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderPhoto
from .filters import apply_artistic_filter


@receiver(post_save, sender=OrderPhoto)
def generate_filtered_photo(sender, instance, created, **kwargs):
    """Photo upload hote hi automatically artistic filter apply karke filtered_image save kar deta hai."""
    if instance.original_image and not instance.filtered_image:
        filtered_file = apply_artistic_filter(instance.original_image, target_name=f"{instance.id}_filtered.jpg")
        instance.filtered_image.save(filtered_file.name, filtered_file, save=False)
        OrderPhoto.objects.filter(pk=instance.pk).update(filtered_image=instance.filtered_image)
