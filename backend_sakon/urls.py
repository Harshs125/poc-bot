from django.urls import path
from . import views
# from .views import Organization, OrganizationEmployer, Configurations, Schedules
urlpatterns = [
    path('add_employer', views.create_organization_employer, name='add_employer'),
    path('add_org', views.add_organization, name='add_organization'),
    path('configurations', views.Configuration.as_view(), name='configurations'),
    path('configurations/<int:config_id>/', views.Configuration.as_view(), name='configurations_update'),
    path('schedules', views.Schedule.as_view(), name='schedules'),
    path('schedules/<int:schedule_id>/', views.Schedule.as_view(), name='schedules_update'),
]