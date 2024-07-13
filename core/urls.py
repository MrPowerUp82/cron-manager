from django.urls import path
from . import views

urlpatterns = [
    path('', views.cron_jobs, name="cron_jobs"),
]
