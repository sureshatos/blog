from django.db import models

# Create your models here.


class Birthplace(models.Model):
    city = models.CharField(max_length=75)
    state = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.city},{self.state}'


class Person(models.Model):
    name = models.CharField(max_length=50)
    bp = models.ForeignKey(Birthplace,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
