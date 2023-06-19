from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
from pymongo import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
import random
import string
from .serializers import (
    ConfigurationSerializer,
    SchedulerSerializer,
    EmployeesSerializer,
    OrganizationSerializer,
    DepartmentSerializer,
    JobsSerializer,
    DownloadSerializer,
    FileValidatorSerializer,
    UploadValidatorSerializer,
    TemplateValidatorSerializer,
    SignUpSerializer,
    EmpDeptSerializer,
    ServiceProviderSerializer,
    
)
from .models import (
    Organization,
    Employee,
    Configuration,
    Schedule,
    Department,
    Jobs,
    DownloadReport,
    FileValidationReport,
    UploadReport,
    TemplateValidationReport,
    SignUpInfo,
    EmpDept,
    ServiceProvider,
    
)

from .downloadscript import download_file_script

client = MongoClient("mongodb://localhost:27017/")
db = client["scheduler"]
queue = db["job_queue"]
# Set up MongoDBJobStore
jobstore = MongoDBJobStore(collection="jobs", database="scheduler")
# Set up BackgroundScheduler with MongoDBJobStore
scheduler = BackgroundScheduler(jobstores={"mongo": jobstore})
scheduler.start()



class SignupAPI(generics.ListAPIView):
    
    queryset = SignUpInfo.objects.all()
    serializer_class = SignUpSerializer
    pagination_class = PageNumberPagination
    
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else: 
                return JsonResponse({"error": "Ivalid data"}, status=400)    
            return JsonResponse({"message": "Data added successfully","data": serializer.data,}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)    
    
    def put(self, request,id):
        try:
            signup = SignUpInfo.objects.get(id=id)
            serializer = SignUpSerializer(signup, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else: 
                return JsonResponse({"error": "Ivalid data"}, status=400)    
            return JsonResponse({"message": "Data updated successfully","data": serializer.data,}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    def delete(self, request,id):
        try:
            signup = SignUpInfo.objects.get(id=id)
            signup.delete()
            return JsonResponse({"message": "Data deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    
class EmployeesAPI(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeesSerializer
    pagination_class = PageNumberPagination


    

    def post(self, request):
        
        try:    
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.sample(characters, 6))
            print("this is password------------>>>>>",password)
            
            
            role=request.data.get("role")
            if role=="SUPERADMIN":
                
                org_id = request.data.get("org")
                org_id_present = Organization.objects.filter(id=org_id).exists()
                if org_id_present:
                    pass
                else:
                    return JsonResponse({"error": "Organization does not exist"}, status=400)
                
                serializer = EmployeesSerializer(data={"name":request.data.get("name"), "email":request.data.get("email"), "password":password, "type":"ADMIN", "org":org_id})
                
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return JsonResponse({"message": "successfully entered data in db"}, status=200)

                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)  
                
            elif role == "ADMIN": 
                
                dept=Department.objects.filter(id=request.data.get("Department"))
                if dept is None:
                    return JsonResponse({"error": "Department does not exist"}, status=400)
                
                org= dept.org  
                serializer = EmployeesSerializer(data={"name":request.data.get("name"), "email":request.data.get("email"), "password":password, "type":"USER", "org":org})
                
                try:
                    serializer.is_valid(raise_exception=True)
                    employee=serializer.save()
                    
                    dept.employee_count+=1
                    dept.save()
                    
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)    
                
                empdeptserializer = EmpDeptSerializer(data={"emp":employee.id, "dept":dept.id})
                
                try:
                    empdeptserializer.is_valid(raise_exception=True)
                    empdeptserializer.save()
                    return JsonResponse({"message": "successfully entered data in db"}, status=200)
                except Exception as e:
                    return JsonResponse({"error1": str(e)}, status=400)             
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)    
            
        
                    
        
        
        
    def put(self, request, id):
        try:
            emp=Employee.objects.get(id=id)
            
            serializer = EmployeesSerializer(emp, data={"name":request.data.get("name"), "email":request.data.get("email"), "password":request.data.get("password")}, partial=True)
            
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return JsonResponse({"message": "successfully updated admin information"}, status=200)

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)  
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    def delete(self, request, id):
        try:
            employee = Employee.objects.get(id=id)
            
            departments=EmpDept.objects.filter(emp=employee.id)
            
            for department in departments:
                department.employee_count -= 1
                department.save()
            
            employee.delete()
            return JsonResponse({"message": "successfully deleted data in db"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class DepartmentAPI(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = PageNumberPagination
    
    def post(self, request):
        
        
        try:
            org_id = request.data.get("org")
            org_id_present = Organization.objects.filter(id=org_id).exists()
            if org_id_present:
                pass
                serializer = DepartmentSerializer(data=request.data, partial=True)
                
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return JsonResponse(
                        {
                            "message": "successfull entered data in db",
                            "data": serializer.data,
                        },
                        status=201,
                    )
                else:
                    return JsonResponse({"error": serializer.errors}, status=400)
                
            else:
                return JsonResponse({"error": "Organization does not exist"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)    
        
        
        
        
    def put(self, request, id):
        try:
            department = Department.objects.get(id=id)
            serializer = DepartmentSerializer(department, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Department updated successfully"}, status=200)
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except Exception as e:
            return Response({"error":str(e)}, status=404)
        
    def delete(self, request, id):
        try:
            department = Department.objects.get(id=id)
            department.delete()
            return Response({"message": "Department deleted successfully"}, status=200)    
        except Exception as e:
            return Response({"error":str(e)}, status=404)

class OrganizationAPI(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        org_id = self.kwargs.get("id")
        if org_id:
            return Organization.objects.filter(id=org_id)
        return Organization.objects.all()

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "successfully entered data in db","data": serializer.data}, status=200
                )
            else:
                return JsonResponse({"error": "Invalid data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    def put(self, request, id):
        try:
            org = Organization.objects.get(id=id)
            serializer = OrganizationSerializer(org, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "successfully entered data in db","data": serializer.data}, status=200
                )
            else:
                return JsonResponse({"error": "Invalid data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)   
        
    def delete(self, request, id):
        try:
            org = Organization.objects.get(id=id)
            org.delete()
            return JsonResponse({"message": "successfully deleted."}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class ServiceProviderAPI(generics.ListAPIView):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    pagination_class = PageNumberPagination
    
    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "successfully entered data in db","data": serializer.data}, status=200
                )
            else:
                return JsonResponse({"error": "Invalid data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
    def put(self, request, id):
        try:
            sp = ServiceProvider.objects.get(id=id)
            serializer = ServiceProviderSerializer(sp, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "successfully entered data in db","data": serializer.data}, status=200)
            else:
                return JsonResponse({"error": "Invalid data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    def delete(self, request, id):
        try:
            sp = ServiceProvider.objects.get(id=id)
            sp.delete()
            return JsonResponse({"message": "successfully deleted."}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)    

class ConfigurationAPI(APIView):
    pagination_class = PageNumberPagination
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def get_serializer(self, *args, **kwargs):
        return ConfigurationSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            dept_name = request.query_params.get("dept_name")
            scheduled = request.query_params.get("is_scheduled")
            if scheduled is not None:
                if str(scheduled) == "true":
                    scheduled = True
                else:
                    scheduled = False
            carrier_name = request.query_params.get("carrier_name")
            configurations = Configuration.objects.filter(
                Q(dept_name=dept_name) if dept_name else Q(),
                Q(is_scheduled=scheduled) if scheduled is not None else Q(),
                Q(carrier=carrier_name) if carrier_name else Q(),
            )
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(configurations, request)
            serializer = ConfigurationSerializer(result_page, many=True)
            response_data = []
            for d in serializer.data:
                response_data.append(
                    {
                        "id": d.get("id"),
                        "ConfigurationName": d.get("name"),
                        "department": d.get("dept_name"),
                        "emp": d.get("emp"),
                        "email": d.get("email"),
                        "carrierName": d.get("carrier"),
                        "schedulingStatus": d.get("is_scheduled"),
                        "scheduler_id": d.get("schedule"),
                    }
                )
            return JsonResponse(
                {
                    "count": paginator.page.paginator.count,
                    "previous": paginator.get_previous_link(),
                    "next": paginator.get_next_link(),
                    "data": response_data,
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def post(self, request, *args, **kwargs):
        try:
            serializer = ConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {
                        "message": "successfull entered data in db",
                        "data": serializer.data,
                    },
                    status=201,
                )
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, id, *args, **kwargs):
        try:
            config = Configuration.objects.get(id=id)
        except Configuration.DoesNotExist:
            return Response({"error": "Invalid Configuration ID"}, status=404)
        serializer = self.get_serializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Configuration updated successfully"})
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class ScheduleAPI(APIView):
    queryset = Schedule.objects.all()
    serializer_class = SchedulerSerializer
    pagination_class = PageNumberPagination

    def get_serializer(self, *args, **kwargs):
        return SchedulerSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            emp = request.query_params.get("emp_id")
            config = request.query_params.get("config_id")
            schedules = Schedule.objects.filter(
                Q(emp=emp) if emp else Q(),
                Q(configurations__icontains=config) if config else Q(),
            )
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(schedules, request)
            data = []
            for schedule in result_page:
                configurations = Configuration.objects.filter(
                    id__in=schedule.configurations
                ).values_list("name", flat=True)
                configuration_names = list(configurations)
                if len(configuration_names) != 0:
                    data.append(
                        {
                            "id": schedule.id,
                            "schedule_name": schedule.schedularName,
                            "emp": schedule.emp.id,
                            "configuration": configuration_names,
                            "interval": f"{schedule.interval} {schedule.weekDay if schedule.weekDay is not None else ''} at {schedule.timeDuration if schedule.timeDuration is not None else ''}",
                            "time": schedule.timeDuration,
                            "weekDay": schedule.weekDay,
                            "monthDay": schedule.monthDay,
                            "timeZone": str(schedule.timeZone),
                            "created_at": schedule.created_at,
                            "updated_at": schedule.updated_at,
                        }
                    )
            return JsonResponse(
                {
                    "count": paginator.page.paginator.count,
                    "previous": paginator.get_previous_link(),
                    "next": paginator.get_next_link(),
                    "data": data,
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request):
        try:
            serializer = SchedulerSerializer(data=request.data)
            if serializer.is_valid():
                conf_already_scheduled = Configuration.objects.filter(
                    id__in=request.data.get("configurations"), is_scheduled=True
                ).exists()
                if conf_already_scheduled:
                    return JsonResponse(
                        {"message": "One or more configurations are already scheduled"},
                        status=400,
                    )
                try:
                    configurations = Configuration.objects.filter(
                        id__in=request.data.get("configurations")
                    )
                    serializer.save()
                    configurations.update(
                        is_scheduled=True, schedule_id=serializer.data.get("id")
                    )
                    queue.insert_one({"schedule_id": serializer.data.get("id")})
                except Exception as e:
                    return JsonResponse({"message": str(e)}, status=400)

                return JsonResponse(
                    {
                        "message": "successfull entered data in db",
                        "data": serializer.data,
                    },
                    status=201,
                )
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, id, *args, **kwargs):
        try:
            schedule = Schedule.objects.get(id=id)
        except Schedule.DoesNotExist:
            return Response({"error": "Invalid Scheduler ID"}, status=404)
        serializer = SchedulerSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Scheduler updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class JobsAPI(APIView):
    def get(self, request):
        jobs = Jobs.objects.all()
        serializer = JobsSerializer(jobs, many=True)
        data = []
        for d in serializer.data:
            configuration = Configuration.objects.get(id=d.get("configuration"))
            schedule = Schedule.objects.get(id=d.get("schedule"))
            data.append(
                {
                    "id": d.get("id"),
                    "Scheduler_Name": schedule.schedularName,
                    "Configuration_Name": configuration.name,
                    "Department_Name": d.get("department_name"),
                    "Service": d.get("service"),
                    "Status": d.get("status"),
                    "Triggered_At": d.get("Triggered_At"),
                }
            )
        return JsonResponse({"data": data}, status=200)

    def post(self, request):
        serializer = JobsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "successfully entered data in db", "data": serializer.data},
                status=200,
            )
        else:
            return JsonResponse({"error": serializer.errors}, status=400)

    def put(self, request, id):
        try:
            job = Jobs.objects.get(id=id)
        except Configuration.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = JobsSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Jobs updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class DownloadSubtaskAPI(APIView):
    def get(self, request, jobid):
        try:
            download = DownloadReport.objects.filter(job=jobid)
        except DownloadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid job id"}, status=400)
        serializer = DownloadSerializer(download, many=True)
        return JsonResponse({"message": "success", "data": serializer.data}, status=200)

    def post(self, request):
        serializer = DownloadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "created download"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, jobid):
        try:
            donwload = DownloadReport.objects.get(job=jobid)
        except DownloadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = DownloadSerializer(donwload, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "Download report updated successfully"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class FileValidatorAPI(APIView):
    def get(self, request, jobid):
        try:
            filevalidate = FileValidationReport.objects.filter(job=jobid)
        except FileValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid job id"}, status=400)
        serializer = FileValidatorSerializer(filevalidate, many=True)
        return JsonResponse({"message": "success", "data": serializer.data}, status=200)

    def post(self, request):
        serializer = FileValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "created FileValidation report"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, jobid):
        try:
            filevalidate = FileValidationReport.objects.get(job=jobid)
        except FileValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = FileValidatorSerializer(
            filevalidate, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "Filevalidation report updated successfully"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class TemplateValidatorAPI(APIView):
    def get(self, request, jobid):
        try:
            templatevalidate = TemplateValidationReport.objects.filter(job=jobid)
        except TemplateValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid job id"}, status=400)
        serializer = TemplateValidatorSerializer(templatevalidate, many=True)
        return JsonResponse({"message": "success", "data": serializer.data}, status=200)

    def post(self, request):
        serializer = TemplateValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "created TemplateValidation report"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, jobid):
        try:
            templatevalidate = TemplateValidationReport.objects.get(job=jobid)
        except TemplateValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = TemplateValidatorSerializer(
            templatevalidate, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "Templatevalidation report updated successfully"},
                status=200,
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class UploadValidatorAPI(APIView):
    def get(self, request, jobid):
        try:
            uploadreport = UploadReport.objects.filter(job=jobid)
        except UploadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid job id"}, status=400)
        serializer = UploadValidatorSerializer(uploadreport, many=True)
        return JsonResponse({"message": "success", "data": serializer.data}, status=200)

    def post(self, request):
        serializer = UploadValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "created Upload report"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def put(self, request, jobid):
        try:
            upload = UploadReport.objects.get(job=jobid)
        except UploadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = UploadValidatorSerializer(upload, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "Upload report updated successfully"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

# Set up MongoDB connection
# Define function to add schedule to MongoDB queue




@csrf_exempt
def add_schedule_to_queue(request, id):
    # Check if schedule_id already exists in the queue
    try:
        if queue.find_one({"schedule_id": id}):
            return JsonResponse({"message": "Schedule already exists in queue."})
        # Add new schedule to the queue
        queue.insert_one({"schedule_id": id})
        return JsonResponse({"message": "Schedule added to queue."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Define function to run scheduler in a separate thread
def run_scheduler_thread():
    while True:
        # Fetch next schedule from MongoDB queue
        try:
            next_job = queue.find_one_and_delete({})
            print(next_job)
            if next_job is not None:
                try:
                    schedule_id = next_job["schedule_id"]
                except Exception as e:
                    print(f"An error occurred: {e}")
                # Check if job already exists for schedule ID
                if not scheduler.get_job(str(schedule_id)):
                    # Fetch schedule and configuration data in same query
                    try:
                        schedule = Schedule.objects.get(id=schedule_id)
                    except Exception as e:
                        print("An error occurred: {e}")
                    # schedule = Schedule.objects.select_related('configurations').get(id=schedule_id)
                    print(schedule)

                    configurations_int = []
                    configurations_list = schedule.configurations
                    for config in configurations_list:
                        configurations_int.append(int(config))

                    if schedule is not None:
                        # Determine cron trigger based on schedule interval and parameters
                        cron_trigger = None
                        if schedule.interval == "DAILY":
                            cron_trigger = CronTrigger(
                                hour=schedule.timeDuration.hour,
                                minute=schedule.timeDuration.minute,
                                second=0,
                                timezone=schedule.timeZone,
                            )
                        elif schedule.interval == "WEEKLY":
                            cron_trigger = CronTrigger(
                                day_of_week=schedule.weekDay,
                                hour=schedule.timeDuration.hour,
                                minute=schedule.timeDuration.minute,
                                second=0,
                                timezone=schedule.timeZone,
                            )
                        elif schedule.interval == "MONTHLY":
                            cron_trigger = CronTrigger(
                                day=schedule.monthDay,
                                hour=schedule.timeDuration.hour,
                                minute=schedule.timeDuration.minute,
                                second=0,
                                timezone=schedule.timeZone,
                            )
                        print(cron_trigger)
                        if cron_trigger is not None:
                            # configuration = schedule.configurations
                            try:
                                job = scheduler.add_job(
                                    download_file_script,
                                    trigger=cron_trigger,
                                    args=[configurations_int, schedule_id],
                                    id=str(schedule_id),
                                )
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                # Push the schedule ID back into the queue
                                queue.insert_one({"schedule_id": schedule_id})
                                print(
                                    f"Schedule ID {schedule_id} pushed back into the queue"
                                )

                            print(f"Added job: {job}")
                            print("All jobs in scheduler:", scheduler.get_jobs())
                            print(scheduler.get_job(str(schedule_id)))
            else:
                break
        except Exception as e:
            print(f"An error occurred: {e}")


# Start BackgroundScheduler in separate thread

scheduler_thread = None


@csrf_exempt
def run_thread(request):
    global scheduler_thread
    if scheduler_thread and scheduler_thread.is_alive():
        return JsonResponse({"message": "Scheduler is already running."})

    scheduler_thread = threading.Thread(target=run_scheduler_thread)
    scheduler_thread.start()
    return JsonResponse({"message": "Scheduler started."})


@csrf_exempt
def stop_thread(request):
    global scheduler_thread
    if scheduler_thread is not None and scheduler_thread.is_alive():
        scheduler_thread.terminate()  # Forcefully stop the thread

        scheduler_thread.join()  # Wait for the thread to finish
        scheduler_thread = None
        return JsonResponse({"message": "Scheduler stopped."})
    else:
        return JsonResponse({"message": "Scheduler is not running."})
