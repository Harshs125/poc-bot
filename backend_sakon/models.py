from django.db import models
from django.utils import timezone


class SuperAdmin(models.Model):
    email = models.EmailField(null=False, unique=True)
    name = models.CharField(null=False, max_length=250)
    password = models.CharField(null=False, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Organization(models.Model):
    name = models.CharField(null=False, max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Employee(models.Model):
    email = models.EmailField(null=False, unique=True)
    name = models.CharField(null=False, max_length=250)
    password = models.CharField(null=False, max_length=250)
    type = models.CharField(null=False, max_length=250)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Carrier(models.Model):
    name = models.CharField(max_length=250, null=False, unique=True)
    website_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AdminOrganization(models.Model):
    admin = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("admin_id", "org_id")


class Department(models.Model):
    name = models.CharField(null=False, max_length=250)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("name", "org_id")


class EmpDept(models.Model):
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("dept_id", "emp_id")


class Schedule(models.Model):
    schedularName = models.CharField(max_length=250, null=False, unique=True)
    configurations = models.JSONField()
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    TASK_FREQUENCY_CHOICES = [
        ("DAILY", 1),
        ("WEEKLY", 2),
        ("MONTHLY", 3),
    ]
    interval = models.CharField(max_length=10, choices=TASK_FREQUENCY_CHOICES)
    timeDuration = models.TimeField()
    weekDay = models.CharField(max_length=250, null=True)
    monthDay = models.IntegerField(null=True)
    timeZone = models.CharField(max_length=50, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Configuration(models.Model):
    name = models.CharField(null=False, max_length=250, unique=True)
    dept_name = models.CharField(null=False, max_length=250)
    email = models.EmailField(null=False)
    password = models.CharField(max_length=250, null=False)
    sftp_login = models.CharField(max_length=250, null=False)
    sftp_password = models.CharField(max_length=250, null=False)
    sftp_path = models.CharField(max_length=500, null=False)
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    carrier = models.CharField(max_length=250, null=False)
    website_url = models.URLField()
    template = models.FileField(upload_to="files/")
    is_scheduled = models.BooleanField(default=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FileMetaData(models.Model):
    name = models.CharField(max_length=250, null=False, unique=True)
    size = models.IntegerField(null=False)
    type = models.CharField(max_length=250, null=False)
    config = models.ForeignKey(Configuration, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
