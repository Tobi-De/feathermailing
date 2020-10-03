import csv
from io import StringIO

from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django_extensions.db.fields import RandomCharField, AutoSlugField
from django_q.tasks import schedule, async_task

from .utils import async_mass_mailing_csv, async_mass_mailing_contact


class Contact(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class CSVFile(models.Model):
    uuid = RandomCharField(length=12)
    file = models.FileField(upload_to="csv_files/")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uuid


# TODO option to nofif admin when email is sent
class Context(models.Model):
    name = models.CharField(max_length=130, unique=True)
    slug = AutoSlugField(populate_from=["name"])
    csv_files = models.ManyToManyField(CSVFile, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_email_count(self):
        # return the numbers of emails
        return self.contact_count + self.emails_from_csv_file_count

    @property
    def csv_file_count(self):
        # return the numbers of csv files
        return self.csv_files.all().count()

    @cached_property
    def emails_from_csv_file_count(self):
        # return the numbers of csv files
        if not self.csv_files:
            return 0
        count = 0
        for csv_upload in self.csv_files.all():
            src = csv_upload.file.read().decode("utf-8")
            reader = csv.reader(StringIO(src), delimiter=",")
            next(reader)
            count += len(list(reader))
        return count

    @property
    def contact_count(self):
        # return the numbers of contact
        return self.contacts.all().count()

    def get_absolute_url(self):
        return reverse("context_detail", kwargs={"slug": self.slug})

    def setup_mail_sending(self, subject, message, dispatch_date, schedule_params):
        if dispatch_date:
            schedule(
                name=f"{self.name}_{dispatch_date.date().replace('/', '_')}",
                func=self.send_mails,
                subject=subject,
                message=message,
                **schedule_params,
            )
        else:
            self.send_mails(subject=subject, message=message)

    # noinspection PyTypeChecker
    def send_mails(self, subject, message):
        for csv_upload in self.csv_files.all():
            async_task(
                func=async_mass_mailing_csv,
                subject=subject,
                message=message,
                from_mail=None,
                csv_file=csv_upload.file,
            )
        async_task(
            func=async_mass_mailing_contact,
            subject=subject,
            message=message,
            from_mail=None,
            contacts=self.contacts.all(),
        )
