from .models import Context


def async_send_mails(context_id, subject, message):
    context = Context.objects.get(id=context_id)
    context.send_mails(subject, message)
