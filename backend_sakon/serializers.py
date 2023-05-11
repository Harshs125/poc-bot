from rest_framework import serializers
from .models import Configuration,Employee,Schedule

class ConfigurationSerializer(serializers.ModelSerializer):
    emp = serializers.CharField(source='emp.id', read_only=True)
    class Meta:
        model = Configuration
        fields = ('name', 'dept_name', 'email', 'password', 'sftp_login', 'sftp_password', 'carrier_name', 'website_url', 'template', 'sftp_path', 'emp',)

    def create(self, validated_data):
        emp_id = self.context.get('request').data.get('created-by-empid')
        employee = Employee.objects.get(id=emp_id)
        validated_data['emp'] = employee
        return Configuration.objects.create(**validated_data)
        
class SchedulerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Schedule
        fields=('name','frequency','time','days_of_week','day_of_month','timezone','config_id','emp_id')
    def create(self, validated_data):
        emp_id = self.context.get('request').data.get('created-by-empid')
        employee = Employee.objects.get(id=emp_id)
        validated_data['emp'] = employee
        return Schedule.objects.create(**validated_data)