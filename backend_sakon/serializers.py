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
    ServiceProvider,
    SignUpInfo,
    EmpDept,
)


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
    
    

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignUpInfo
        fields=(
            "id",
            "email",
            "organization",
            "designation",
            "department_count",
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
            "created_at",
            "updated_at",
            
        )

    def create(self, validated_data):
        return Schedule.objects.create(**validated_data)
    
class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = (  
            "id",
            "name",
            "department",
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
            "org",
            "created_at",
            "updated_at"
        )

    def create(self, validated_data):
        return Configuration.objects.create(**validated_data)

class JobsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Jobs
        fields = (
            "id",
            "department",
            "organization",
            "service",
            "status",
            "Triggered_At",
            "configuration",
            "schedule",
            "emp"
            # "interval"
        )

    def create(self, validated_data):
        return Jobs.objects.create(**validated_data)


class DownloadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DownloadReport
        fields = ("id", "job", "status", "description","department","organization","attempts", "Triggered_At"
                #   ,"interval"
                  )

    def create(self, validated_data):
        return DownloadReport.objects.create(**validated_data)


class FileValidatorSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = FileValidationReport
        fields = ("id", "job", "status", "description","department","organization","attempts", "Triggered_At"
                #   ,"interval"
                  )

    def create(self, validated_data):
        return FileValidationReport.objects.create(**validated_data)


class UploadValidatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = UploadReport
        fields = ("id", "job", "status", "description","department","organization","attempts", "Triggered_At"
                #   ,"interval"
                  )

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
            "department",
            "organization",
            "attempts",
            "Triggered_At",
            "variance"
            # ,"interval"
        )

    def create(self, validated_data):
        return TemplateValidationReport.objects.create(**validated_data)
