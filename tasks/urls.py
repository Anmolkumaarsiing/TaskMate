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
    path('task-completion-graph/', views.task_completion_graph, name='task_completion_graph'),
    path('mark-completed/<int:task_id>/', views.mark_completed, name='mark_completed'),
    path('change-status/<int:task_id>/', views.change_status, name='change_status'),
     path('task-status-graph/', views.task_status_graph, name='task_status_graph'),
]
