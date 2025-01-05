# TaskMate/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls')),  # Include tasks URLs
    path('', RedirectView.as_view(url='/tasks/', permanent=False)),  # Redirect root URL to /tasks/
]
