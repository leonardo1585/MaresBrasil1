from django.db import models

# Create your models here.
class Lugar(models.Model):
    lugar = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)


    def __str__(self):
        return self.lugar