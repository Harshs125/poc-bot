from rest_framework import serializers
from .models import (
    Configuration,
    Employee,
    Schedule,
    Organization,
    Department,
    Jobs,
    DownloadReport,
    FileValidationReport,
    TemplateValidationReport,
    UploadReport,
    SignUpInfo,
    EmpDept,
    ServiceProvider,
    
)


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = (
            "id",
            "name",
            "dept_name",
            "email",
            "password",
            "sftp_login",
            "sftp_password",
            "carrier",
            "website_url",
            "template",
            "sftp_path",
            "emp",
            "is_scheduled",
            "schedule",
        )

    def create(self, validated_data):
        return Configuration.objects.create(**validated_data)


class SchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "id",
            "schedularName",
            "interval",
            "timeDuration",
            "weekDay",
            "monthDay",
            "timeZone",
            "configurations",
            "emp",
        )

    def create(self, validated_data):
        return Schedule.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.schedularName = validated_data.get(
            "schedularName", instance.schedularName
        )
        instance.interval = validated_data.get("interval", instance.interval)
        instance.timeDuration = validated_data.get(
            "timeDuration", instance.timeDuration
        )
        instance.weekDay = validated_data.get("weekDay", instance.weekDay)
        instance.monthDay = validated_data.get("monthDay", instance.monthDay)
        instance.timeZone = validated_data.get("timeZone", instance.timeZone)
        instance.configurations = validated_data.get(
            "configurations", instance.configurations
        )
        instance.emp_id = validated_data.get("emp_id", instance.emp_id)
        instance.save()
        return instance


class EmployeesSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "password", "email", "type", "org")

    def create(self, validated_data):
        return Employee.objects.create(**validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name","department_count","service_providers")

    def create(self, validated_data):
        return Organization.objects.create(**validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name","employee_count", "org")

    def create(self, validated_data):
        return Department.objects.create(**validated_data)

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ("id", "name", "url")
        
    def create(self, validated_data):
        return ServiceProvider.objects.create(**validated_data)    

class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = (
            "id",
            "department_name",
            "service",
            "status",
            "Triggered_At",
            "configuration",
            "schedule",
        )

    def create(self, validated_data):
        return Jobs.objects.create(**validated_data)


class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadReport
        fields = ("id", "job", "status", "description", "attempts", "Triggered_At")

    def create(self, validated_data):
        return DownloadReport.objects.create(**validated_data)


class FileValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileValidationReport
        fields = ("id", "job", "status", "description", "attempts", "Triggered_At")

    def create(self, validated_data):
        return FileValidationReport.objects.create(**validated_data)


class UploadValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadReport
        fields = ("id", "job", "status", "description", "attempts", "Triggered_At")

    def create(self, validated_data):
        return UploadReport.objects.create(**validated_data)


class TemplateValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateValidationReport
        fields = (
            "id",
            "job",
            "status",
            "description",
            "attempts",
            "Triggered_At",
            "variance",
        )

    def create(self, validated_data):
        return TemplateValidationReport.objects.create(**validated_data)


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUpInfo
        fields=(
            "id",
            "email",
            "organization",
            "designation",
            "employee_count",
            "service_providers",
        )
        
        def create(self, validated_data):
            return SignUpInfo.objects.create(**validated_data)
        
        
class EmpDeptSerializer(serializers.ModelSerializer):
    class Meta:
        model=EmpDept
        fields=(
            "emp",
            "dept"
        )
        
    def create(self,validated_data):
        return EmpDept.objects.create(**validated_data)        
    
