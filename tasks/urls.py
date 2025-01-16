from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),  # Route for the home page
    path('login/', views.login_view, name='login'),  # Route for login
    path('signup/', views.signup_view, name='signup'),  # Route for signup
    path('dashboard/', views.dashboard, name='dashboard'),  # Route for dashboard
    path('logout/', views.logout_view, name='logout'),  # Route for logout
    path('AddTask/', views.add_task, name='AddTask'),  # Route for adding task
    path('task-section/', views.task_section_view, name='task_section'),  #Route for task sections
    path('mark-completed/<int:task_id>/', views.mark_completed, name='mark_completed'),
    path('change-status/<int:task_id>/', views.change_status, name='change_status'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('task-status-graph/', views.task_status_graph, name='task_status_graph'),
    path('task-alerts/', views.task_alert, name='task_alert'),  # Task Alerts page
    path('profile/', views.profile_view, name='profile'),
]