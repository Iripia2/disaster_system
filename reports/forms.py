from django import forms
from .models import DisasterReport, Location, MediaAttachment, Comment, ResponderAssignment
from accounts.models import CustomUser


class AnonymousReportForm(forms.Form):
    reporter_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional reporter name'}))
    phone_number = forms.CharField(required=False, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional phone number'}))
    category = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'class': 'form-select'}), required=True)
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief incident title'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the incident'}))
    severity = forms.ChoiceField(choices=DisasterReport.SEVERITY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    lga = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LGA'}))
    affected_count = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}))
    incident_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}))
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = DisasterReport._meta.get_field('category').remote_field.model.objects.filter(is_active=True)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['address', 'city', 'lga', 'landmark', 'latitude', 'longitude']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'lga': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Local Government Area'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nearest landmark (optional)'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Latitude (optional)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Longitude (optional)'}),
        }


class DisasterReportForm(forms.ModelForm):
    class Meta:
        model = DisasterReport
        fields = ['title', 'category', 'description', 'severity', 'affected_count', 'incident_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title of the incident'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the disaster in detail — cause, extent, what happened...'
            }),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'affected_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'incident_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class MediaAttachmentForm(forms.ModelForm):
    class Meta:
        model = MediaAttachment
        fields = ['file', 'file_type', 'caption']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional caption'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment or field update...'
            }),
        }


class AssignResponderForm(forms.ModelForm):
    responder = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='responder', is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Select Responder'
    )

    class Meta:
        model = ResponderAssignment
        fields = ['responder', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes for the responder (optional)'
            }),
        }


class UpdateStatusForm(forms.ModelForm):
    class Meta:
        model = ResponderAssignment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Field update notes...'
            }),
        }
