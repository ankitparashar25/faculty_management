from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.faculty_login, name='login'),
    path('logout/', views.faculty_logout, name='logout'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),
    path('admin/add_faculty/', login_required(views.add_faculty), name='add_faculty'),
    path('admin/add_schedule/', login_required(views.add_schedule), name='add_schedule'),
    path('admin/edit_schedule/<int:schedule_id>/', login_required(views.edit_schedule), name='edit_schedule'),
    path('admin/delete_schedule/<int:schedule_id>/', login_required(views.delete_schedule), name='delete_schedule'),
    path('admin/verify_profiles/', login_required(views.verify_profiles), name='verify_profiles'),
    path('profile/', login_required(views.profile), name='profile'),
    path('schedule/', login_required(views.schedule), name='schedule'),
    path('admin/view_profile/<int:user_id>/', login_required(views.admin_view_profile), name='admin_view_profile'),
    path('admin/edit_profile/<int:user_id>/', login_required(views.admin_edit_profile), name='admin_edit_profile'),
    path('request_reschedule/<int:schedule_id>/', login_required(views.request_reschedule), name='request_reschedule'),
    path('manage_reschedule/<int:request_id>/', login_required(views.manage_reschedule), name='manage_reschedule'),
]
