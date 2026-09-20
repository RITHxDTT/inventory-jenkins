from django.db import models
class CatalogModel(models.Model):
    name = models.CharField(max_length=180)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
        ordering = ['name']
    def __str__(self):
        return self.name
