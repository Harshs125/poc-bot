from django.urls import path
from . import views

urlpatterns = [
    path("employees", views.EmployeesAPI.as_view(), name="employee"),
    path("employees/<int:id>", views.EmployeesAPI.as_view(), name="employee"),
    path("organizations", views.OrganizationAPI.as_view(), name="add_organization"),
    path(
        "organizations/<int:id>",
        views.OrganizationAPI.as_view(),
        name="add_organization",
    ),
    path("configurations", views.ConfigurationAPI.as_view(), name="configurations"),
    path(
        "configurations/<int:id>",
        views.ConfigurationAPI.as_view(),
        name="configurations_update",
    ),
    path("schedules", views.ScheduleAPI.as_view(), name="schedules"),
    path("schedules/<int:id>", views.ScheduleAPI.as_view(), name="schedules_update"),
    path("add_to_queue/<int:id>", views.add_schedule_to_queue, name="add_to_queue"),
    path("run_thread", views.run_thread, name="run_thread"),
    # path("download_file", views.download_file_script, name="download_file_script"),
]
