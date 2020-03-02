from django.contrib import admin

from mailsend.models import MailTemplate

@admin.register(MailTemplate)
class MailTemplate(admin.ModelAdmin):
    list_display = [field.name for field in MailTemplate._meta.fields]
