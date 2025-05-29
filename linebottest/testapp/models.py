from django.db import models

# Create your models here.
class Drink(models.Model):
    CATEGORY_CHOICES = [
        ('tea', '茶類'),
        ('milk', '奶類'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='飲料名稱')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', verbose_name='類別')
    description = models.TextField(verbose_name='介紹')
    image_url = models.URLField(blank=True, verbose_name='圖片網址')

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = '飲料'
        verbose_name_plural = '飲料'
