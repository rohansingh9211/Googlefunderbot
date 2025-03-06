from django.contrib import admin

from enfund_view.models import Message, User, googledrive

# Register your models here.
admin.site.register(User)
admin.site.register(googledrive)
admin.site.register(Message)