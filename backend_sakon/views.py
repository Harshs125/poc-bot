from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.utils import IntegrityError
from django.db.models import F,Q
from .serializers import ConfigurationSerializer,SchedulerSerializer
from .models import Organization,Employee, Configuration, Schedule


@csrf_exempt 
def create_organization_employer(request): 
    if request.method == 'POST': 
        try: 
            data = json.loads(request.body) 
            org_id = data.get('org_id') 
            org_instance = Organization.objects.get(id=org_id) 
            organization_employer = Employee.objects.create( 
                email=data['emp_email'], 
                name=data['emp_name'], 
                password=data['emp_password'], 
                type=data['emp_type'], 
                org_id=org_instance.id  
            ) 
            return JsonResponse({'success': True, 'message': 'Organization employer added successfully'}) 
        except Organization.DoesNotExist: 
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
            name = data.get('name') 
            Organization.objects.create( 
                name=name, 
            ) 
            return JsonResponse({'success': True, 'message': 'Organization added successfully'}) 
        except Exception as e: 
            return JsonResponse({'success': False, 'message': str(e)}) 
    else: 
        return JsonResponse({'success': False, 'message': 'Invalid request method'})



class ConfigurationAPI(APIView):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    def get_serializer(self, *args, **kwargs):
        return ConfigurationSerializer(*args, **kwargs)
    def get(self, request,*args, **kwargs):
        try:
            dept_name = request.query_params.get('dept_name')
            is_scheduled = request.query_params.get('is_scheduled') 
            configurations=Configuration.objects.filter(
                Q(dept_name=dept_name) if dept_name else Q(),
                Q(is_scheduled=is_scheduled) if is_scheduled is not None else Q()
            )
            serializer=ConfigurationSerializer(configurations, many=True)
            data = [{
                'config_id': configuration.id,
                'config_name': configuration.name,
                'dept_name': configuration.dept_name,
                'email': configuration.email,
                'created_by_empid': configuration.emp.id,
                'carrier_name': configuration.carrier_name,
                'is_scheduled': configuration.is_scheduled,
            } for configuration in configurations]
            return JsonResponse({'configurations': data, 'total_rows': configurations.count()})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    def post(self, request, *args, **kwargs):
        try:
            serializer = ConfigurationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message':'successfull entered data in db','data':serializer.data}, status=201)
            else:
                return JsonResponse({'error':serializer.errors}, status=400)
        except Exception as e:
            return Response({'error': str(e)})
        
        
    def put(self, request, config_id, *args, **kwargs):
        try:
            config = Configuration.objects.get(id=config_id)
        except Configuration.DoesNotExist:
            return Response({'error': 'Invalid Configuration ID'}, status=404)
        serializer = self.get_serializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Configuration updated successfully'})
        else:
            return Response(serializer.errors, status=400)

class ScheduleAPI(APIView): 
    queryset = Schedule.objects.all()
    serializer_class = SchedulerSerializer
    def get_serializer(self, *args, **kwargs):
        return SchedulerSerializer(*args, **kwargs)
    def get(self, request, *args, **kwargs): 
        try:
            emp = request.query_params.get('emp_id') 
            config = request.query_params.get('config_id') 
            schedules = Schedule.objects.filter(
                Q(emp=emp) if emp else Q(),
                Q(config_id=config) if config is not None else Q()
            ) 
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
            print(request.data)
            emp = request.data.get('emp_id') 
            configs = request.data.get('configs') 
            schedule_name=request.data.get('schedule_name') 
            interval = request.data.get('interval') 
            time = request.data.get('time') 
            days_of_week = request.data.get('days_of_week', None) 
            day_of_month = request.data.get('day_of_month', None) 
            timezone = request.data.get('timezone', 'UTC') 
            
            for config in configs:
                schedule = Schedule.objects.create( 
                emp_id=emp, 
                config_id=config, 
                name=schedule_name, 
                frequency=interval, 
                time=time, 
                days_of_week=days_of_week, 
                day_of_month=day_of_month, 
                timezone=timezone 
                ) 
                schedule.save() 
                config=Configuration.objects.get(id=config)
                config.is_scheduled = True
                config.save()
            return JsonResponse({'success': "success fully inserted data in db"},status=200) 
        except Exception as e:
            return JsonResponse({'error': str(e)},status=400) 
 
    def put(self, request,schedule_id,*args, **kwargs): 
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response({'error': 'Invalid Scheduler ID'}, status=404)
        serializer = self.get_serializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Scheduler updated successfully'})
        else:
            return Response(serializer.errors, status=400)
        