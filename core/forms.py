from django import forms
from tinymce.widgets import TinyMCE

from .models import Context, Contact, EmailTemplate


class CSVFileUploadForm(forms.Form):
    csv_files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )


class ContextForm(forms.ModelForm):
    class Meta:
        model = Context
        fields = ["name", "contacts"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"] = forms.CharField(
            widget=TinyMCE(attrs={"cols": 80, "rows": 30})
        )


class EmailForm(forms.Form):
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea)
    dispatch_date = forms.DateTimeField(
        required=False, help_text="first run, keep empty to send now"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"] = forms.CharField(
            widget=TinyMCE(attrs={"cols": 80, "rows": 30})
        )


class EmailTemplateChooserForm(forms.Form):
    template = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["template"].choices = tuple(
            [
                (template.slug, template.subject)
                for template in EmailTemplate.objects.all()
            ]
        )


class LoadEmailForm(forms.Form):
    file = forms.FileField()
