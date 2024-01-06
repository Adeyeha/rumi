from django.contrib import admin

# Register your models here.
from .models import PetChoice,InterestChoice

admin.site.register(PetChoice)
admin.site.register(InterestChoice)