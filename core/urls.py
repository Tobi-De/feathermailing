from django.urls import path

from .views import (
    context_list,
    context_create,
    context_update,
    send_mails,
    context_detail,
    context_delete,
    contact_create,
    contact_delete,
    contact_list,
    email_template_list,
    email_template_create,
    email_template_update,
    email_template_delete,
    load_email,
    event_list
)

urlpatterns = [
    path("", context_list, name="context_list"),
    path("context-detail/<str:slug>/", context_detail, name="context_detail"),
    path("context-delete/<str:slug>/", context_delete, name="context_delete"),
    path("context-update/<str:slug>/", context_update, name="context_update"),
    path("add-context/", context_create, name="context_create"),
    path("add-contact/", contact_create, name="contact_create"),
    path("send-mails/<str:slug>/", send_mails, name="send_mails"),
    path("contact-delete/<str:email>/", contact_delete, name="contact_delete"),
    path("contact-list/", contact_list, name="contact_list"),
    path("email-template-list/", email_template_list, name="email_template_list"),
    path("email-template-create/", email_template_create, name="email_template_create"),
    path("email-template-update/<str:slug>/", email_template_update, name="email_template_update"),
    path("email-template-delete/<str:slug>/", email_template_delete, name="email_template_delete"),
    path("load-email/", load_email, name="load_email"),
    path("event-list/", event_list, name="event_list")
]
