from django import forms

from .models import Context, Contact


class CSVFileUploadForm(forms.Form):
    csv_files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )


class ContextForm(forms.ModelForm):
    class Meta:
        model = Context
        fields = ["name", "contacts"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"


class EmailForm(forms.Form):
    # type (O)nce, M(I)nutes, (H)ourly, (D)aily, (W)eekly, (M)onthly, (Q)uarterly, (Y)early
    REPEAT_CHOICES = ((-1, "Always"), (0, "Never"), (1, "Number"))
    SCHEDULE_TYPE = (
        ("O", "Once"),
        ("M", "Minutes"),
        ("H", "Hourly"),
        ("D", "Daily"),
        ("W", "Weekly"),
        ("M", "Monthly"),
        ("Q", "Quaterly"),
        ("Y", "Yearly"),
    )
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea)
    dispatch_date = forms.DateTimeField(
        required=False, help_text="first run, keep empty to send now"
    )
    schedule_type = forms.ChoiceField(choices=SCHEDULE_TYPE)
    repeats_type = forms.ChoiceField(
        choices=REPEAT_CHOICES,
        help_text="if you choose 'Number' you need to set a 'Repeat Nbr'",
    )
    repeats_nbr = forms.IntegerField(
        initial=1,
        help_text="Number of time to repeat the "
                  "sending process, has effect only if your "
                  "schedule type is not 'Once' and repeat is 'Number'",
        min_value=1,
    )
    minutes = forms.IntegerField(
        help_text="This field has effect only if your schedule type is 'Minutes' ",
        min_value=1,
        initial=1,
    )

    def generate_schedule_params(self):
        params_dict = {
            "schedule_type": self.cleaned_data.get("schedule_type"),
        }
        if self.cleaned_data.get("schedule_type") == "M":
            params_dict["minutes"] = (self.cleaned_data.get("minutes"),)
        params_dict["repeats"] = (
            self.cleaned_data.get("repeats_nbr")
            if self.cleaned_data.get("repeat_type") == 1
            else self.cleaned_data.get("repeats_type")
        )
        return params_dict
