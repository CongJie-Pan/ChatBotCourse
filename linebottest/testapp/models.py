from django.db import models

# Create your models here.
class Drink(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
