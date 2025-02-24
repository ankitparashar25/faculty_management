from django import forms
from django.contrib.auth.models import User
from .models import FacultyProfile, Schedule, RescheduleRequest
from django.utils import timezone

class AddFacultyForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = FacultyProfile
        fields = ['photo', 'documents', 'department', 'phone_number']

class ScheduleForm(forms.ModelForm):
    faculty = forms.ModelChoiceField(
        queryset=User.objects.filter(facultyprofile__isnull=False),
        label="Select Faculty"
    )
    duration = forms.DurationField(
        label="Duration",
        help_text="Format: HH:MM:SS"
    )
    
    class Meta:
        model = Schedule
        fields = ['faculty', 'title', 'date', 'start_time', 'end_time', 'duration']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'label': 'Date'}),




            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')

        if start_time and end_time and date:
            from datetime import datetime
            now = datetime.now()
            schedule_start = datetime.combine(date, start_time)
            schedule_end = datetime.combine(date, end_time)

            if schedule_end <= schedule_start:
                raise forms.ValidationError("End time must be after start time")
            
            # Update duration based on validated times
            cleaned_data['duration'] = schedule_end - schedule_start

        return cleaned_data





class RescheduleRequestForm(forms.ModelForm):
    class Meta:
        model = RescheduleRequest
        fields = ['date', 'new_start_time', 'new_end_time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'new_start_time': forms.TimeInput(attrs={'type': 'time'}),
            'new_end_time': forms.TimeInput(attrs={'type': 'time'}),

            'reason': forms.Textarea(attrs={'rows': 3}),
        }
