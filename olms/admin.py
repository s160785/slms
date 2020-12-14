from django.contrib import admin
from .models import UserProfile, Leaves, Personal_info, Outing, Counts

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Leaves)
admin.site.register(Personal_info)
admin.site.register(Outing)
admin.site.register(Counts)
