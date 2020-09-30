import csv
from io import StringIO

from django.core.mail import send_mass_mail
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django_extensions.db.fields import RandomCharField, AutoSlugField


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

    def get_emails_from_csv(self):
        if not self.csv_files:
            return []
        emails = []
        for csv_upload in self.csv_files.all():
            emails += self.extract_emails_from_csv(csv_upload.file)
        return emails

    def get_all_emails(self):
        emails = self.get_emails_from_csv()
        emails += [contact.email for contact in self.contacts.all()]
        return emails

    # noinspection PyTypeChecker
    def send_mails(self, subject, message, dispatch_date):
        send_mass_mail(
            ((subject, message, None, [email]) for email in self.get_emails_from_csv())
        )

    @classmethod
    def extract_emails_from_csv(cls, csv_file):
        source_file = csv_file.read().decode("utf-8")
        reader = csv.reader(StringIO(source_file), delimiter=",")
        header = next(reader)
        index = header.index("email")
        return [line[index] for line in reader]
