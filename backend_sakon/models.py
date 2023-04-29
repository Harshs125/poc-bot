from django.db import models

# Create your models here.
from django.db import models 
from django.utils import timezone 
# from django_timezone_field import TimeZoneField
# Create your models here. 
 
class SuperAdmin(models.Model): 
    superadmin_id=models.AutoField(primary_key=True) 
    superadmin_email=models.EmailField(null=False,unique=True) 
    superadmin_name=models.CharField(null=False,max_length=250) 
    superadmin_password=models.CharField(null=False,max_length=250) 
    created_at=models.DateTimeField(auto_now_add=True) 
    modified_at=models.DateTimeField(auto_now=True) 
 
class Organizations(models.Model): 
    org_id=models.AutoField(primary_key=True) 
    organization_name=models.CharField(null=False,max_length=250,unique=True) 
    created_at=models.DateTimeField(auto_now_add=True) 
    modified_at=models.DateTimeField(auto_now=True) 
 
 
class OrganizationEmployers(models.Model): 
    emp_id=models.AutoField(primary_key=True) 
    emp_email=models.EmailField(null=False,unique=True) 
    emp_name=models.CharField(null=False,max_length=250) 
    emp_password=models.CharField(null=False,max_length=250) 
    emp_type=models.CharField(null=False,max_length=250) 
    org=models.ForeignKey(Organizations,on_delete=models.SET_NULL,null=True) 
    created_at=models.DateTimeField(auto_now_add=True) 
    modified_at=models.DateTimeField(auto_now=True) 
 
 
class AdminOrganization(models.Model): 
    admin=models.ForeignKey(OrganizationEmployers,on_delete=models.SET_NULL,null=True) 
    org=models.ForeignKey(Organizations,on_delete=models.SET_NULL,null=True) 
    created_at=models.DateTimeField(auto_now_add=True) 
    modified_at=models.DateTimeField(auto_now=True) 
 
    class Meta: 
        unique_together=('admin_id','org_id') 
 
 
 
class Departments(models.Model): 
    dept_id=models.AutoField(primary_key=True) 
    dept_name=models.CharField(null=False,max_length=250) 
    org=models.ForeignKey(Organizations,on_delete=models.SET_NULL,null=True) 
     
    class Meta: 
        unique_together=('dept_name','org_id') 
 
 
class EmpDept(models.Model): 
    id=models.AutoField(primary_key=True) 
    emp=models.ForeignKey(OrganizationEmployers,on_delete=models.SET_NULL,null=True) 
    dept=models.ForeignKey(Departments,on_delete=models.SET_NULL,null=True) 
 
    class Meta: 
        unique_together=('dept_id','emp_id') 
        
        
class Configurations(models.Model): 
    config_id=models.AutoField(primary_key=True) 
    config_name=models.CharField(null=False,max_length=250)
    dept_name=models.CharField(null=False,max_length=250)
    email=models.EmailField(null=False) 
    password=models.CharField(max_length=250,null=False) 
    sftp_login=models.CharField(max_length=250,null=False)
    sftp_password=models.CharField(max_length=250,null=False)
    emp=models.ForeignKey(OrganizationEmployers,on_delete=models.SET_NULL,null=True) 
    carrier_name=models.CharField(max_length=250,null=False) 
    website_url=models.CharField(max_length=1000,null=False) 
    template=models.FileField(upload_to='files/') 
    is_scheduled=models.BooleanField(default=False)
    sftp_path=models.CharField(max_length=500,null=False) 
    created_at=models.DateTimeField(auto_now_add=True) 
    updated_at=models.DateTimeField(auto_now=True) 
 
class FileMetaData(models.Model): 
    file_id=models.AutoField(primary_key=True) 
    file_name=models.CharField(max_length=250,null=False,unique=True) 
    file_size=models.IntegerField(null=False) 
    file_type=models.CharField(max_length=250,null=False) 
    file_by_empid=models.ForeignKey(OrganizationEmployers,on_delete=models.SET_NULL,null=True) 
    carrier_name=models.CharField(max_length=250,null=False) 
    sftp_location_path=models.CharField(max_length=500,null=False) 
    created_at=models.DateTimeField(auto_now_add=True) 
    modified_at=models.DateTimeField(auto_now=True) 
 
class Schedules(models.Model): 
    schedule_id=models.AutoField(primary_key=True) 
    schedule_name=models.CharField(max_length=250,null=False,unique=True)
    config=models.ForeignKey(Configurations,on_delete=models.SET_NULL,null=True) 
    emp=models.ForeignKey(OrganizationEmployers,on_delete=models.SET_NULL,null=True) 
    TASK_FREQUENCY_CHOICES = [ 
        ('daily', 'Daily'), 
        ('weekly', 'Weekly'), 
        ('monthly', 'Monthly'), 
    ] 
    frequency = models.CharField(max_length=10, choices=TASK_FREQUENCY_CHOICES) 
    time = models.TimeField() 
    days_of_week = models.CharField(max_length=50, blank=True, null=True) 
    day_of_month = models.DateField(blank=True, null=True) 
    timezone=models.CharField(max_length=50,default='UTC')
    created_at=models.DateTimeField(auto_now_add=True) 
    updated_at=models.DateTimeField(auto_now=True) 