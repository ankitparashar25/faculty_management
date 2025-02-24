from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import logging

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.utils import timezone

from .models import FacultyProfile, Schedule, RescheduleRequest
from .forms import ProfileUpdateForm, ScheduleForm, AddFacultyForm, RescheduleRequestForm

def landing_page(request):
    return render(request, 'faculty/landing_page.html')

def faculty_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                profile = FacultyProfile.objects.get(user=user)
                if profile.is_verified:
                    messages.success(request, 'Login successful! Your account is verified.')
                else:
                    messages.warning(request, 'Login successful! Your account verification is pending.')
            except FacultyProfile.DoesNotExist:
                messages.warning(request, 'Login successful! Please complete your profile.')
                
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'faculty/login.html')

def faculty_logout(request):
    logout(request)
    return redirect('landing_page')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')
    return render(request, 'faculty/admin_login.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    faculty_profiles = FacultyProfile.objects.all()
    add_faculty_form = AddFacultyForm()
    pending_requests = RescheduleRequest.objects.filter(status='Pending')
    
    selected_faculty_id = request.GET.get('faculty')
    schedules = []
    selected_faculty = None
    
    if selected_faculty_id:
        try:
            selected_faculty = User.objects.get(id=selected_faculty_id)
            schedules = Schedule.objects.filter(faculty=selected_faculty).order_by('-date', 'start_time')
            for schedule in schedules:
                if schedule.duration:
                    total_seconds = int(schedule.duration.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    schedule.duration_display = f"{hours}h {minutes}m"
                else:
                    schedule.duration_display = "N/A"
        except User.DoesNotExist:
            messages.error(request, 'Invalid faculty selected')
    
    return render(request, 'faculty/admin_dashboard.html', {

        'faculty_profiles': faculty_profiles,
        'add_faculty_form': add_faculty_form,
        'schedules': schedules,
        'selected_faculty': selected_faculty,
        'pending_requests': pending_requests
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_faculty(request):
    if request.method == 'POST':
        form = AddFacultyForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            FacultyProfile.objects.create(user=user)
            messages.success(request, 'Faculty added successfully!')
            return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            faculty_id = request.POST.get('faculty')
            if faculty_id:
                try:
                    faculty = User.objects.get(id=faculty_id)
                    schedule.faculty = faculty
                    schedule.save()
                    messages.success(request, 'Schedule added successfully!')
                    return redirect('admin_dashboard')
                except User.DoesNotExist:
                    messages.error(request, 'Invalid faculty selected')
                    return redirect('admin_dashboard')
    else:
        form = ScheduleForm()
    
    faculty_id = request.GET.get('faculty')
    if faculty_id:
        faculty = get_object_or_404(User, id=faculty_id)
        schedules = Schedule.objects.filter(faculty=faculty).order_by('-date', 'start_time')
        form.fields['faculty'].initial = faculty_id
    else:
        schedules = Schedule.objects.none()
        
    return render(request, 'faculty/add_schedule.html', {
        'form': form,
        'schedules': schedules
    })

@login_required
def verify_profiles(request):
    unverified_profiles = FacultyProfile.objects.filter(is_verified=False)
    
    if request.method == 'GET':
        profile_id = request.GET.get('profile_id')
        if profile_id:
            try:
                profile = get_object_or_404(FacultyProfile, id=profile_id)
                profile.is_verified = True
                profile.save()
                messages.success(request, f'Profile for {profile.user.username} verified successfully!')
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f'Error verifying profile: {str(e)}')
                return redirect('admin_dashboard')
    
    return render(request, 'faculty/verify_profiles.html', {
        'unverified_profiles': unverified_profiles
    })

@login_required
def profile(request):
    profile, created = FacultyProfile.objects.get_or_create(user=request.user)
    
    schedules = Schedule.objects.filter(faculty=request.user).order_by('-date', 'start_time')
    for schedule in schedules:
        if schedule.duration:
            total_seconds = int(schedule.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            schedule.duration_display = f"{hours}h {minutes}m"
        else:
            schedule.duration_display = "N/A"
    
    completed_schedules = [s for s in schedules if s.get_status() == 'Completed']
    in_progress_schedules = [s for s in schedules if s.get_status() == 'In Progress']
    upcoming_schedules = [s for s in schedules if s.get_status() == 'Upcoming']


    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.department = form.cleaned_data['department']
            profile.phone_number = form.cleaned_data['phone_number']
            profile.save()
            
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
    return render(request, 'faculty/profile.html', {
        'form': form,
        'completed_schedules': completed_schedules,
        'in_progress_schedules': in_progress_schedules,
        'upcoming_schedules': upcoming_schedules
    })

@login_required
def schedule(request):
    faculty_id = request.GET.get('faculty_id')
    
    if faculty_id:
        faculty = get_object_or_404(User, id=faculty_id)
        schedules = Schedule.objects.filter(faculty=faculty).order_by('-date', 'start_time')
    else:
        faculty = request.user
        schedules = Schedule.objects.filter(faculty=request.user).order_by('-date', 'start_time')
    
    for schedule in schedules:
        if schedule.duration:
            total_seconds = int(schedule.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            schedule.duration_display = f"{hours}h {minutes}m"
        else:
            schedule.duration_display = "N/A"
    
    all_faculty = User.objects.filter(is_staff=False).order_by('username')
            
    if request.method == 'POST' and 'confirm_schedule' in request.POST:
        schedule_id = request.POST.get('schedule_id')
        logger = logging.getLogger(__name__)
        logger.debug(f"Attempting to confirm schedule ID: {schedule_id}")
        try:
            schedule = Schedule.objects.get(id=schedule_id, faculty=request.user)
            logger.debug(f"Found schedule: {schedule.title}")
            schedule.is_confirmed = True
            schedule.confirmed_at = timezone.now()
            schedule.save()
            logger.debug(f"Schedule confirmed at: {schedule.confirmed_at}")
            messages.success(request, 'Schedule confirmed successfully!')
        except Schedule.DoesNotExist:
            logger.error(f"Schedule not found: {schedule_id}")
            messages.error(request, 'Invalid schedule selected')

    return render(request, 'faculty/schedule.html', {
        'schedules': schedules,
        'selected_faculty': faculty,
        'all_faculty': all_faculty
    })

@login_required
def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'faculty/add_schedule.html', {
        'form': form,
        'edit_mode': True
    })

def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('admin_dashboard')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_view_profile(request, user_id):
    profile = get_object_or_404(FacultyProfile, user__id=user_id)
    return render(request, 'faculty/admin_profile_view.html', {'profile': profile})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_edit_profile(request, user_id):
    profile = get_object_or_404(FacultyProfile, user__id=user_id)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'faculty/admin_profile_edit.html', {
        'form': form,
        'profile': profile
    })

@login_required
def request_reschedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    if request.method == 'POST':
        form = RescheduleRequestForm(request.POST)
        if form.is_valid():
            reschedule_request = form.save(commit=False)
            reschedule_request.schedule = schedule
            reschedule_request.requested_by = request.user
            reschedule_request.save()
            messages.success(request, 'Reschedule request submitted successfully!')
            return redirect('schedule')
    else:
        form = RescheduleRequestForm()
    
    return render(request, 'faculty/request_reschedule.html', {
        'form': form,
        'schedule': schedule
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_reschedule(request, request_id):
    reschedule_request = get_object_or_404(RescheduleRequest, id=request_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            reschedule_request.status = 'Approved'
            messages.success(request, 'Reschedule request approved!')
        elif action == 'reject':
            reschedule_request.status = 'Rejected'
            messages.success(request, 'Reschedule request rejected!')
        reschedule_request.save()
        return redirect('admin_dashboard')
    
    return render(request, 'faculty/manage_reschedule.html', {
        'request': reschedule_request
    })
