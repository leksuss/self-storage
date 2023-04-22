from django.contrib import admin

from .models import User, Box, TransferRequest, Promocodes

admin.site.register(User)
admin.site.register(Box)
admin.site.register(TransferRequest)
admin.site.register(Promocodes)