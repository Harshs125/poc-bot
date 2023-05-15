from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.db.utils import IntegrityError
from django.db.models import Q
from .serializers import ConfigurationSerializer,SchedulerSerializer,EmployeesSerializer,OragnizationSerializer
from .models import Organization,Employee, Configuration, Schedule


class EmployeesAPI(APIView):
   
    def get(self,request,id=None):
        if id is not None:
           employees=Employee.objects.get(id=id)
           serializer=EmployeesSerializer(employees)
        else:
           employees=Employee.objects.all()
           serializer=EmployeesSerializer(employees,many=True)
        print(type(serializer.data))
        return JsonResponse({'data':serializer.data},status=200)

    def post(self,request):
        print("ee")
        serializer=EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"successfully entered data in db"},status=200)
        else:
            return JsonResponse({"error":serializer.errors},status=400)       


class OrganizationAPI(APIView):
   
    def get(self,request,id=None):
        if id is not None:
           organization=Organization.objects.get(id=id)
           serializer=OragnizationSerializer(organization)
        else:
           organization=Organization.objects.all()
           serializer=OragnizationSerializer(organization,many=True)
        print(type(serializer.data))
        return JsonResponse({'data':serializer.data},status=200)

    def post(self,request):
        serializer=EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"successfully entered data in db"},status=200)
        else:
            return JsonResponse({"error":serializer.errors},status=400)       


class ConfigurationAPI(APIView):
    queryset=Configuration.objects.all()
    serializer_class=ConfigurationSerializer
    def get_serializer(self, *args, **kwargs):
        return ConfigurationSerializer(*args, **kwargs)
    
    def get(self, request,*args, **kwargs):
        try:
            dept_name=request.query_params.get('dept_name')
            is_scheduled=request.query_params.get('is_scheduled') 
            configurations=Configuration.objects.filter(
                Q(dept_name=dept_name) if dept_name else Q(),
                Q(is_scheduled=is_scheduled) if is_scheduled is not None else Q()
            )
            serializer=ConfigurationSerializer(configurations, many=True)
            data = [{
                'name':configuration.name,
                'dept_name':configuration.dept_name,
                'emp':configuration.emp.id,
                'email':configuration.email,
                'carrier_name':configuration.carrier_name,
                'is_scheduled':configuration.is_scheduled,
            } for configuration in configurations]
            return JsonResponse({'configurations':data,'total_rows':configurations.count()})
        except Exception as e:
            return JsonResponse({'error':str(e)})
        
    def post(self, request, *args, **kwargs):
        try:
            serializer=ConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message':'successfull entered data in db','data':serializer.data},status=201)
            else:
                return JsonResponse({'error':serializer.errors},status=400)
        except Exception as e:
            return Response({'error':str(e)})
        
    def put(self, request,id, *args, **kwargs):
        try:
            config=Configuration.objects.get(id=id)
        except Configuration.DoesNotExist:
            return Response({'error': 'Invalid Configuration ID'},status=404)
        serializer=self.get_serializer(config,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Configuration updated successfully'})
        else:
            return JsonResponse({'errors':serializer.errors},status=400)


class ScheduleAPI(APIView): 
    queryset=Schedule.objects.all()
    serializer_class=SchedulerSerializer
    def get_serializer(self, *args, **kwargs):
        return SchedulerSerializer(*args, **kwargs)
    
    def get(self, request, *args, **kwargs): 
        try:
            emp=request.query_params.get('emp_id') 
            config=request.query_params.get('config_id') 
            schedules=Schedule.objects.filter(
                Q(emp=emp) if emp else Q(),
                Q(config=config) if config is not None else Q()
            ) 
            data=[{ 
                'id':schedule.id, 
                'name':schedule.name, 
                'emp':schedule.emp, 
                'config':schedule.config, 
                'frequency':schedule.frequency, 
                'time':schedule.time, 
                'day_of_week':schedule.days_of_week, 
                'day_of_month':schedule.day_of_month, 
                'timezone':str(schedule.timezone), 
                'created_at':schedule.created_at, 
                'updated_at':schedule.updated_at, 
                } for schedule in schedules] 
            return JsonResponse({'schedules': data,'total_rows': schedules.count()}) 
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
    def post(self, request): 
        try:
            emp=request.data.get('emp_id') 
            configs=request.data.get('configs') 
            schedule_name=request.data.get('schedule_name') 
            interval=request.data.get('interval') 
            time=request.data.get('time') 
            days_of_week=request.data.get('days_of_week', None) 
            day_of_month=request.data.get('day_of_month', None) 
            timezone=request.data.get('timezone', 'UTC') 
            schedules = []
            for config_id in configs:
                schedules.append(
                    Schedule(
                        emp=emp,
                        config=config_id,
                        name=schedule_name,
                        frequency=interval,
                        time=time,
                        days_of_week=days_of_week,
                        day_of_month=day_of_month,
                        timezone=timezone
                    )
                )
            Schedule.objects.bulk_create(schedules)
            Configuration.objects.filter(id__in=configs).update(is_scheduled=True)
            return JsonResponse({'success': "success fully inserted data in db"},status=200) 
        except Exception as e:
            return JsonResponse({'error': str(e)},status=400) 
 
    def put(self, request,id,*args, **kwargs): 
        try:
            schedule = Schedule.objects.get(id=id)
        except Schedule.DoesNotExist:
            return Response({'error': 'Invalid Scheduler ID'},status=404)
        serializer = SchedulerSerializer(schedule, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Scheduler updated successfully'},status=200)
        else:
            return Response(serializer.errors,status=400)