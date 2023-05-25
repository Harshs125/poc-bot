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
    path("departments",views.departmentAPI.as_view(),name="departments")
]
