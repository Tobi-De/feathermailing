from django import forms

from .models import Context, Contact


class CSVFileUploadForm(forms.Form):
    csv_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class ContextForm(forms.ModelForm):
    class Meta:
        model = Context
        fields = ["name", "contacts"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class EmailForm(forms.Form):
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea)
    dispatch_date = forms.DateTimeField(required=False)
