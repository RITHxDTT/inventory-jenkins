from django.conf import settings
from django.db import models
from common.forms import validate_image
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profiles/', blank=True, validators=[validate_image])
    def __str__(self):
        return self.user.get_username()
