from django.db import models

# Create your models here.
class Image(models.Model):
	pic = models.FileField(upload_to='MiniApp_Images')