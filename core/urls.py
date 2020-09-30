from django.urls import path

from .views import (
    context_list,
    context_create,
    send_mails,
    context_detail,
    context_delete,
    contact_create,
)

urlpatterns = [
    path("", context_list, name="context_list"),
    path("context-detail/<str:slug>/", context_detail, name="context_detail"),
    path("context-delete/<str:slug>/", context_delete, name="context_delete"),
    path("add-context/", context_create, name="context_create"),
    path("add-contact/", contact_create, name="contact_create"),
    path("send-mails/<str:slug>/", send_mails, name="send_mails"),
]
