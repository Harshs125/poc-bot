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
    path("departments", views.DepartmentAPI.as_view(), name="departments"),
    path("jobs",views.JobsAPI.as_view(),name="Jobs"),
    path("jobs/<int:id>",views.JobsAPI.as_view(),name="Jobs update"),
    path("jobs/report/download/<int:jobid>",views.DownloadSubtaskAPI.as_view(),name="download report"),
    path("jobs/report/filevalidation/<int:jobid>",views.FileValidatorAPI.as_view(),name="file validation report"),
    path("jobs/report/templatevalidation/<int:jobid>",views.TemplateValidatorAPI.as_view(),name="template validation report"),
    path("jobs/report/upload/<int:jobid>",views.UploadValidatorAPI.as_view(),name="upload validation"),
    path("jobs/report/download",views.DownloadSubtaskAPI.as_view(),name="download report"),
    path("jobs/report/filevalidation",views.FileValidatorAPI.as_view(),name="file validation report"),
    path("jobs/report/templatevalidation",views.TemplateValidatorAPI.as_view(),name="template validation report"),
    path("jobs/report/upload",views.UploadValidatorAPI.as_view(),name="upload validation"),
    
    
    path("run_thread", views.run_thread, name="run_thread"),
    path("stop_thread", views.stop_thread, name="stop_thread"),
    path("add_to_queue/<int:id>", views.add_schedule_to_queue, name="add_to_queue"),
]
