from django.db import models

# Create your models here.
class Student(models.Model):
    sName = models.CharField(max_length=20, null=False)
    sSex = models.CharField(max_length=2, default='M', null=False)
    sBirthday = models.DateField(null=False)
    sEmail = models.EmailField(max_length=50, blank=True, default='')
    sPhone = models.CharField(max_length=20, blank=True, default='')
    sAddress = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.sName
