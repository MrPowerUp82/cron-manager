from django.urls import path
from . import views

urlpatterns = [
    path('', views.cron_jobs, name="cron_jobs"),
    path('custom_crons/', views.custom_crons, name="custom_crons"),
]
