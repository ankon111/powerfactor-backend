from django.contrib import admin
from .models import Plant
from .models import Datapoint


admin.site.register(Plant)
admin.site.register(Datapoint)
