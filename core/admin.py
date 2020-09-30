from django.contrib import admin

from .models import Context, Contact, CSVFile

admin.site.register(Contact)
admin.site.register(Context)
admin.site.register(CSVFile)
