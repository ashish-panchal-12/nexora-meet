from django import forms
from .models import Meeting


class MeetingForm(forms.ModelForm):
    class Meta:
        model  = Meeting
        fields = ['title', 'description', 'scheduled_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control custom-input',
                'placeholder': 'e.g. Team Standup, Project Review...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control custom-input',
                'rows': 3,
                'placeholder': 'Brief description (optional)',
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'form-control custom-input',
                'type': 'datetime-local',
            }),
        }


class JoinMeetingForm(forms.Form):
    meeting_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control custom-input join-input',
            'placeholder': 'XXX-XXXX-XXX',
            'autocomplete': 'off',
        })
    )