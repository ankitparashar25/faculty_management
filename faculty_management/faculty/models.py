from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    documents = models.FileField(upload_to='faculty_documents/', blank=True, null=True)
    employee_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Schedule(models.Model):
    faculty = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField(default=date.today)

    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            from datetime import datetime
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            if end < start:
                end = datetime.combine(self.date + timedelta(days=1), self.end_time)
            self.duration = end - start
        super().save(*args, **kwargs)


    def get_status(self):
        from datetime import datetime
        now = datetime.now()
        schedule_start = datetime.combine(self.date, self.start_time)
        schedule_end = datetime.combine(self.date, self.end_time)
        
        # Handle cases where end time is on the next day
        if schedule_end < schedule_start:
            schedule_end = schedule_end.replace(day=schedule_end.day + 1)
            
        if not self.is_confirmed:
            return 'Not Confirmed'
        elif now < schedule_start:
            return 'Upcoming'
        elif schedule_start <= now <= schedule_end:
            return 'In Progress'
        else:
            return 'Completed'


    def __str__(self):
        return f"{self.title} - {self.faculty.username}"




class RescheduleRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    new_start_time = models.TimeField()
    new_end_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.new_start_time and self.new_end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.date, self.new_start_time)
            end = datetime.combine(self.date, self.new_end_time)
            if end < start:
                end = datetime.combine(self.date + timedelta(days=1), self.new_end_time)
            self.duration = end - start
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Reschedule Request for {self.schedule.title} by {self.requested_by.username}"
