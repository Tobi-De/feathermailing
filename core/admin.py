from django.contrib import admin

from .models import Context, Contact, CSVFile, EmailTemplate, Event

admin.site.register(Contact)
admin.site.register(Context)
admin.site.register(CSVFile)
admin.site.register(EmailTemplate)
admin.site.register(Event)
