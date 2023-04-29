from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.utils import IntegrityError
 # Import your models here
from .models import Organizations, OrganizationEmployers, Configurations, Schedules


@csrf_exempt 
def create_organization_employer(request): 
    if request.method == 'POST': 
        try: 
            data = json.loads(request.body) 
            org_id = data.get('org_id') 
            org_instance = Organizations.objects.get(org_id=org_id) 
            organization_employer = OrganizationEmployers.objects.create( 
                emp_email=data['emp_email'], 
                emp_name=data['emp_name'], 
                emp_password=data['emp_password'], 
                emp_type=data['emp_type'], 
                org_id=org_instance.org_id
            ) 
            return JsonResponse({'success': True, 'message': 'Organization employer added successfully'}) 
        except Organizations.DoesNotExist: 
            return JsonResponse({'success': False, 'message': 'Organization with the provided id does not exist'}) 
        except IntegrityError: 
            return JsonResponse({'success': False, 'message': 'Organization employer with the provided email already exists'}) 
        except Exception as e: 
            return JsonResponse({'success': False, 'message': str(e)}) 
    else: 
        return JsonResponse({'success': False, 'message': 'Invalid request method'}) 
@csrf_exempt 
def add_organization(request): 
    if request.method == 'POST': 
        try: 
            data = json.loads(request.body) 
            org_name = data.get('organization_name') 
            Organizations.objects.create( 
                organization_name=org_name, 
            ) 
            return JsonResponse({'success': True, 'message': 'Organization added successfully'}) 
        except Exception as e: 
            return JsonResponse({'success': False, 'message': str(e)}) 
    else: 
        return JsonResponse({'success': False, 'message': 'Invalid request method'})



class Configuration(APIView):
    def get(self, request, *args, **kwargs):
        try:
            dept_name = request.query_params.get('dept_name')
            is_scheduled = request.query_params.get('is_scheduled')
            configurations = Configurations.objects.all()
            if dept_name:
                configurations = configurations.filter(dept_name=dept_name)
            if is_scheduled:
                configurations = configurations.filter(is_scheduled=is_scheduled)
            data = [{
                'config_id': configuration.config_id,
                'config_name': configuration.config_name,
                'dept_name': configuration.dept_name,
                'email': configuration.email,
                'created_by_empid': configuration.emp_id,
                'carrier_name': configuration.carrier_name,
                'is_scheduled': configuration.is_scheduled,
            } for configuration in configurations]
            return JsonResponse({'configurations': data, 'total_rows': configurations.count()})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    def post(self, request, *args, **kwargs):
        try:
            emp_id = request.POST.get('created-by-empid')
            config_instance = OrganizationEmployers.objects.get(emp_id=emp_id)
            config = Configurations.objects.create(
                config_name=request.POST.get('config-name'),
                dept_name=request.POST.get('dept-name'),
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                sftp_login=request.POST.get('sftp-login'),
                sftp_password=request.POST.get('sftp-password'),
                carrier_name=request.POST.get('carrier-name'),
                website_url=request.POST.get('website-url'),
                template=request.data['template'],
                sftp_path=request.POST.get('sftp-path'),
                emp=config_instance,
            )
            config.save()
            return Response("successfully entered in db")
        except Exception as e:
            return Response({'error': str(e)})
        
        
    def put(self, request, config_id, *args, **kwargs):
        try:
            configuration = Configurations.objects.get(config_id=config_id)
            # update the configuration fields
            configuration.config_name = request.data.get('config_name', configuration.config_name)
            configuration.dept_name = request.data.get('dept-name', configuration.dept_name)
            configuration.email = request.data.get('email', configuration.email)
            configuration.sftp_login = request.data.get('sftp-login', configuration.sftp_login)
            configuration.sftp_password = request.data.get('sftp-password', configuration.sftp_password)
            configuration.sftp_path = request.data.get('sftp-path', configuration.sftp_path)
            configuration.carrier_name = request.data.get('carrier-name', configuration.carrier_name)
            configuration.website_url = request.data.get('website-url', configuration.website_url)
            configuration.template = request.data.get('template', configuration.template)
            configuration.is_scheduled = request.data.get('is_scheduled', configuration.is_scheduled)
            configuration.save()
            data = {
                'config_id': configuration.config_id,
                'config_name': configuration.config_name,
                'dept_name': configuration.dept_name,
                'email': configuration.email,
                'sftp_login': configuration.sftp_login,
                'sftp_password': configuration.sftp_password,
                'sftp_path': configuration.sftp_path,
                'carrier_name': configuration.carrier_name,
                'website_url': configuration.website_url,
               
                'is_scheduled': configuration.is_scheduled,
                'created_at': configuration.created_at,
                'updated_at': configuration.updated_at
            }
            return JsonResponse({'configuration': data})
        except Configurations.DoesNotExist:
            return JsonResponse({'message': 'Configuration not found.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

class Schedule(APIView): 
     
     
    def get(self, request, *args, **kwargs): 
        try:
            emp = request.query_params.get('emp_id') 
            config = request.query_params.get('config_id') 
            schedules = Schedules.objects.all() 
 
            if emp: 
                schedules = schedules.filter(emp_id=emp) 
 
            if config: 
                schedules = schedules.filter(config_id=config) 
 
            data = [{ 
                'schedule_id': schedule.schedule_id, 
                'schedule_name': schedule.schedule_name, 
                'emp_id': schedule.emp_id, 
                'config_id': schedule.config_id, 
                'frequency': schedule.frequency, 
                'time': schedule.time, 
                'day_of_week': schedule.days_of_week, 
                'day_of_month': schedule.day_of_month, 
                'timezone': str(schedule.timezone), 
                'created_at': schedule.created_at, 
                'updated_at': schedule.updated_at, 
                } for schedule in schedules] 
 
            return JsonResponse({'schedules': data,'total_rows': schedules.count()}) 
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
            
    def post(self, request): 
        try:
            data = json.loads(request.body) 
            emp = data.get('emp_id') 
            config = data.get('config_id') 
            schedule_name=data.get('schedule_name') 
            frequency = data.get('frequency') 
            time = data.get('time') 
            days_of_week = data.get('days_of_week', None) 
            day_of_month = data.get('day_of_month', None) 
            timezone = data.get('timezone', 'UTC') 

        
            schedule = Schedules.objects.create( 
                emp_id=emp, 
                config_id=config, 
                schedule_name=schedule_name, 
                frequency=frequency, 
                time=time, 
                days_of_week=days_of_week, 
                day_of_month=day_of_month, 
                timezone=timezone 
             
            ) 
            schedule.save() 
            config=Configurations.objects.get(config_id=config)
            config.is_scheduled = True
            config.save()
            return JsonResponse({'success': True}) 
        except Exception as e:
            return JsonResponse({'error': str(e)}) 
        
    
 
 

 
    def put(self, request, *args, **kwargs): 
        try:
            schedule_id = kwargs.get('schedule_id') 
            if not schedule_id: 
                return JsonResponse({'error': 'schedule_id is required!'}, status=400) 
            try: 
                schedule = Schedules.objects.get(schedule_id=schedule_id) 
            except Schedules.DoesNotExist: 
                return JsonResponse({'error': 'Schedule does not exist!'}, status=404) 
         
         
            data = json.loads(request.body) 
            emp = data.get('emp_id', schedule.emp_id) 
            config = data.get('config_id', schedule.config_id) 
            schedule_name = data.get('schedule_name', schedule.schedule_name) 
            frequency = data.get('frequency', schedule.frequency) 
            time = data.get('time', schedule.time) 
            days_of_week = data.get('days_of_week', schedule.days_of_week) 
            day_of_month = data.get('day_of_month', schedule.day_of_month) 
            timezone = data.get('timezone', schedule.timezone) 
          
            schedule.emp_id = emp 
            schedule.config_id = config 
            schedule.schedule_name = schedule_name 
            schedule.frequency = frequency 
            schedule.time = time 
            schedule.days_of_week = days_of_week 
            schedule.day_of_month = day_of_month 
            schedule.timezone = timezone 
            schedule.save() 
            return JsonResponse({'success': True})     
        except Exception as e:
            return JsonResponse({'error': str(e)})