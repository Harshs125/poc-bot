from rest_framework import serializers
from .models import Configuration,Employee,Schedule,Organization


class ConfigurationSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=Configuration
        fields=('name','dept_name','email','password','sftp_login','sftp_password','carrier_name','website_url','template','sftp_path','emp',)

    def create(self, validated_data):
        return Configuration.objects.create(**validated_data)


class SchedulerSerializer(serializers.ModelSerializer):

    class Meta:
        model=Schedule
        fields=('name','frequency','time','days_of_week','day_of_month','timezone','config_id','emp_id')

    def create(self, validated_data):
        emp_id=self.context.get('request').data.get('created-by-empid')
        validated_data['emp']=emp_id
        return Schedule.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.time = validated_data.get('time', instance.time)
        instance.days_of_week = validated_data.get('days_of_week', instance.days_of_week)
        instance.day_of_month = validated_data.get('day_of_month', instance.day_of_month)
        instance.timezone = validated_data.get('timezone', instance.timezone)
        instance.config_id = validated_data.get('config_id', instance.config_id)
        instance.emp_id = validated_data.get('emp_id', instance.emp_id)
        instance.save()
        return instance

class EmployeesSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    class Meta:
        model=Employee
        fields=('id','name','password','email','type','org')

    def create(self,validated_data):
        return Employee.objects.create(**validated_data)


class OragnizationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Organization
        fields=('id','name')

    def create(self,validated_data):
        return Organization.objects.create(**validated_data)