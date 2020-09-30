from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, View, DetailView, DeleteView, CreateView

from .forms import ContextForm, EmailForm, CSVFileUploadForm
from .models import Context, CSVFile, Contact


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


class ContactCreateView(CreateView):
    model = Contact
    template_name = "core/contact_create.html"
    fields = ["email"]

    def get_success_url(self):
        messages.success(self.request, "Contact Added")
        return reverse("home")


contact_create = ContactCreateView.as_view()


class SendEmailView(LoginRequiredMixin, View):
    template_name = "core/send_mails.html"

    def get_context_object(self):
        # This is the context object
        return get_object_or_404(Context, slug=self.kwargs.get("slug"))

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {"form": EmailForm()})

    def post(self, request, *args, **kwargs):
        form = EmailForm(request.POST)
        context_object = self.get_context_object()
        if form.is_valid():
            context_object.send_mails(**form.cleaned_data)
            messages.success(self.request, "Sending...")
        return render(request, self.template_name, {"form": EmailForm()})


send_mails = SendEmailView.as_view()
