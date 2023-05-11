from django.urls import path
from . import views
# from .views import Organization, OrganizationEmployer, Configurations, Schedules
urlpatterns = [
    path('add-employer', views.create_organization_employer, name='add_employer'),
    path('add-org', views.add_organization, name='add_organization'),
    path('configurations', views.ConfigurationAPI.as_view(), name='configurations'),
    path('configurations/<int:config_id>', views.ConfigurationAPI.as_view(), name='configurations_update'),
    path('schedules', views.ScheduleAPI.as_view(), name='schedules'),
    path('schedules/<int:schedule_id>', views.ScheduleAPI.as_view(), name='schedules_update'),
]