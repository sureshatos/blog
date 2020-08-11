from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Birthplace)
admin.site.register(Person)