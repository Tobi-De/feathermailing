import csv
from io import StringIO
from itertools import islice

from django.core.mail import send_mail
from django.utils.html import strip_tags
from django_q.tasks import async_task


def get_index(iterable, value, default=None):
    try:
        index = iterable.index(value)
    except ValueError:
        return default
    else:
        return index


def async_mass_mailing_csv(
    subject, message, from_mail, csv_file, offset=0, limit=100, size=0
):
    source_file = csv_file.read().decode("utf-8")
    reader = csv.reader(StringIO(source_file), delimiter=",")
    header = next(reader)
    index = header.index("email")
    lines = islice(reader, offset, offset + limit)
    for line in lines:
        send_mail(
            subject,
            message=strip_tags(message),
            from_email=from_mail,
            recipient_list=[line[index]],
            html_message=message,
        )
    if size == 0:
        size = len(list(reader))
    if offset > size:
        return
    async_task(
        async_mass_mailing_csv,
        subject=subject,
        message=message,
        from_mail=from_mail,
        csv_file=csv_file,
        offset=offset + limit,
        limit=limit,
        size=size,
    )


def async_mass_mailing_contact(
    subject, message, from_mail, contacts, offset=0, limit=100
):
    if len(contacts[offset: offset + limit]) > 0:
        for contact in contacts:
            send_mail(
                subject,
                message=strip_tags(message),
                from_email=from_mail,
                recipient_list=[contact.email],
                html_message=message,
            )
        async_task(
            async_mass_mailing_contact,
            subject=subject,
            message=message,
            from_mail=from_mail,
            contacts=contacts,
            offset=offset + limit,
            limit=limit,
        )
