from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import (
    ListView,
    View,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
    FormView,
)
from django_q.tasks import async_task

from .forms import (
    ContextForm,
    EmailForm,
    CSVFileUploadForm,
    LoadEmailForm,
    EmailTemplateChooserForm,
)
from .models import Context, CSVFile, Contact, EmailTemplate


class ContextListView(LoginRequiredMixin, ListView):
    template_name = "core/context_list.html"
    queryset = Context.objects.all().order_by("-created")
    paginate_by = 6


context_list = ContextListView.as_view()


class ContextDetailView(LoginRequiredMixin, DetailView):
    model = Context
    template_name = "core/context_detail.html"
    context_object_name = "context"


context_detail = ContextDetailView.as_view()


class ContextCreateView(LoginRequiredMixin, View):
    template_name = "core/context_create.html"

    def get_context_data(self, **kwargs):
        context = {
            "form": ContextForm(),
            "files_form": CSVFileUploadForm(),
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = ContextForm(request.POST)
        files_form = CSVFileUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist("csv_files")
        if form.is_valid() and files_form.is_valid():
            context = form.save()
            for file in files:
                context.csv_files.add(CSVFile.objects.create(file=file))
                context.save()
            messages.success(request, "Context Created")
            return redirect("context_list")
        return render(request, self.template_name, self.get_context_data())


context_create = ContextCreateView.as_view()


class ContextDeleteView(DeleteView):
    model = Context

    def get_success_url(self):
        messages.success(self.request, "Context Delete")
        return reverse("context_list")


context_delete = ContextDeleteView.as_view()


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    template_name = "core/contact_create.html"
    fields = ["email"]

    def get_success_url(self):
        messages.success(self.request, "Contact Added")
        return reverse("contact_list")


contact_create = ContactCreateView.as_view()


class SendEmailView(LoginRequiredMixin, View):
    template_name = "core/send_mails.html"

    def get_context_object(self):
        # This is the context object
        return get_object_or_404(Context, slug=self.kwargs.get("slug"))

    def get_context_data(self):
        try:
            email_slug = self.request.GET["template"]
        except MultiValueDictKeyError:
            form = EmailForm()
            email_slug = ""
        else:
            email_template = get_object_or_404(EmailTemplate, slug=email_slug)
            form = EmailForm(
                initial={
                    "subject": email_template.subject,
                    "message": email_template.message,
                }
            )
        context = {
            "form": form,
            "template_form": EmailTemplateChooserForm(),
            "slug": self.kwargs.get("slug"),
            "email_slug": email_slug,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            self.get_context_data(),
        )

    def post(self, request, *args, **kwargs):
        form = EmailForm(request.POST)
        context_object = self.get_context_object()
        if form.is_valid():
            async_task(
                context_object.setup_mail_sending,
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
                dispatch_date=form.cleaned_data["dispatch_date"],
                schedule_params=form.generate_schedule_params(),
            )
            messages.success(self.request, "Sending...")
        return render(request, self.template_name, self.get_context_data())


send_mails = SendEmailView.as_view()


class ContactListView(LoginRequiredMixin, ListView):
    template_name = "core/contact_list.html"
    queryset = Contact.objects.all().order_by("-created")
    paginate_by = 6


contact_list = ContactListView.as_view()


class ContactDelete(LoginRequiredMixin, DeleteView):
    model = Contact

    def get_object(self, queryset=None):
        return get_object_or_404(Contact, email=self.kwargs.get("email"))

    def get_success_url(self):
        messages.success(self.request, "Contact Delete")
        return reverse("contact_list")


contact_delete = ContactDelete.as_view()


class EmailTemplateCreate(LoginRequiredMixin, CreateView):
    template_name = "core/email_template_create.html"
    model = EmailTemplate
    fields = "__all__"

    def get_success_url(self):
        messages.success(self.request, "Email template created")
        return reverse("email_template_list")


email_template_create = EmailTemplateCreate.as_view()


class EmailTemplateList(LoginRequiredMixin, ListView):
    template_name = "core/email_template_list.html"
    queryset = EmailTemplate.objects.all().order_by("-created")
    paginate_by = 6


email_template_list = EmailTemplateList.as_view()


class EmailTemplateUpdate(LoginRequiredMixin, UpdateView):
    template_name = "core/email_template_update.html"
    model = EmailTemplate
    fields = "__all__"

    def get_success_url(self):
        messages.success(self.request, "Email template updated")
        return reverse("email_template_list")


email_template_update = EmailTemplateUpdate.as_view()


class EmailTemplateDelete(LoginRequiredMixin, DeleteView):
    model = EmailTemplate
    template_name = "core/email_template_confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Email template delete")
        return reverse("email_template_list")


email_template_delete = EmailTemplateDelete.as_view()


class LoadEmailView(LoginRequiredMixin, FormView):
    template_name = "core/load_email.html"
    form_class = LoadEmailForm

    def form_valid(self, form):
        EmailTemplate.create_email_from_file(form.cleaned_data.get("file"))
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Email created")
        return reverse("email_template_list")


load_email = LoadEmailView.as_view()
