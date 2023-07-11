from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
from pymongo import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, filters
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
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
import string
import random
from .downloadscript import download_file_script
import jwt
from django.conf import settings
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .customAuth import LocalAuth

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
    filter_backends = [filters.SearchFilter]
    search_fields = ["organization"]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return JsonResponse({"error": "Ivalid data"}, status=400)
            return JsonResponse(
                {
                    "message": "Data added successfully",
                    "data": serializer.data,
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, id):
        try:
            signup = SignUpInfo.objects.get(id=id)
            serializer = SignUpSerializer(signup, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            else:
                return JsonResponse({"error": "Ivalid data"}, status=400)
            return JsonResponse(
                {
                    "message": "Data updated successfully",
                    "data": serializer.data,
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, id):
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
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get(self, request, id):
        try:
            emp = Employee.objects.get(id=id)
            employee_info = []
            if emp.type == "SUPERADMIN":
                employees = Employee.objects.filter(type="ADMIN")
                for employee in employees:
                    employee_info.append(
                        {
                            "id": employee.id,
                            "name": employee.name,
                            "email": employee.email,
                            "type": employee.type,
                            "org": employee.org.name,
                        }
                    )

            elif emp.type == "ADMIN":
                employees = Employee.objects.filter(type="USER", org=emp.org)
                for employee in employees:
                    departments = EmpDept.objects.filter(emp=employee.id)
                    department_names = [
                        department.dept.name for department in departments
                    ]
                    employee_info.append(
                        {
                            "id": employee.id,
                            "name": employee.name,
                            "email": employee.email,
                            "type": employee.type,
                            "Department": department_names,
                            "org": emp.org.name,
                        }
                    )

            elif emp.type == "USER":
                departments = EmpDept.objects.filter(emp=emp.id)
                department_names = [department.dept.name for department in departments]

                employee_info.append(
                    {
                        "id": emp.id,
                        "name": emp.name,
                        "email": emp.email,
                        "type": emp.type,
                        "Department": department_names,
                        "org": emp.org.name,
                    }
                )

            return JsonResponse({"employee_info": employee_info}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request):
        try:
            characters = string.ascii_letters + string.digits + string.punctuation
            password = "".join(random.sample(characters, 6))

            role = request.data.get("role")
            if role == "SUPERADMIN":
                org_id = request.data.get("org")
                org_id_present = Organization.objects.filter(id=org_id).exists()
                if org_id_present:
                    pass
                else:
                    return JsonResponse(
                        {"error": "Organization does not exist"}, status=400
                    )

                serializer = EmployeesSerializer(
                    data={
                        "name": request.data.get("name"),
                        "email": request.data.get("email"),
                        "password": password,
                        "type": "ADMIN",
                        "org": org_id,
                    }
                )

                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return JsonResponse(
                        {"message": "successfully entered data in db"}, status=200
                    )
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)

            elif role == "ADMIN":
                department_ids = request.data.get("Department")
                departments = Department.objects.filter(id__in=department_ids)
                if departments.count() != len(department_ids):
                    return JsonResponse(
                        {"error": "One or more departments do not exist"}, status=400
                    )

                department_for_org = Department.objects.get(id=department_ids[0])
                org = department_for_org.org_id

                serializer = EmployeesSerializer(
                    data={
                        "name": request.data.get("name"),
                        "email": request.data.get("email"),
                        "password": password,
                        "type": "USER",
                        "org": org,
                    }
                )
                try:
                    serializer.is_valid(raise_exception=True)
                    employee = serializer.save()

                    for department in departments:
                        empdeptserializer = EmpDeptSerializer(
                            data={"emp": employee.id, "dept": department.id}
                        )
                        try:
                            empdeptserializer.is_valid(raise_exception=True)
                            empdeptserializer.save()
                            department.employee_count += 1
                            department.save()
                        except Exception as e:
                            return JsonResponse({"error": str(e)}, status=400)

                    return JsonResponse(
                        {"message": "successfully entered data in db"}, status=200
                    )
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, id):
        try:
            emp = Employee.objects.get(id=id)
            new_departments = request.data.get("Department")
            if emp.type == "USER" and new_departments:
                new_departments = [int(dept_id) for dept_id in new_departments]
                new_departments_set = set(new_departments)
                # Get the current departments of the employee
                current_departments = EmpDept.objects.filter(emp=emp)
                current_departments_set = set(
                    [dept.dept.id for dept in current_departments]
                )
                # Remove employee from old departments
                for dept in current_departments:
                    if dept.dept.id not in new_departments_set:
                        dept.dept.employee_count -= 1
                        dept.dept.save()
                        dept.delete()
                # Add employee to new departments
                for dept_id in new_departments:
                    if dept_id not in current_departments_set:
                        department = Department.objects.get(id=dept_id)
                        emp_dept = EmpDept(emp=emp, dept=department)
                        emp_dept.save()
                        department.employee_count += 1
                        department.save()
            serializer = EmployeesSerializer(
                emp,
                data={
                    "name": request.data.get("name"),
                    "email": request.data.get("email"),
                },
                partial=True,
            )
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return JsonResponse(
                    {"message": "successfully updated employee information"}, status=200
                )
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, id):
        try:
            employee = Employee.objects.get(id=id)
            departments = EmpDept.objects.filter(emp=employee.id)

            for department in departments:
                department.dept.employee_count -= 1
                department.dept.save()

            employee.delete()
            return JsonResponse(
                {"message": "successfully deleted data in db"}, status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class DepartmentAPI(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        org_id = self.request.query_params.get("org_id")
        if org_id:
            queryset = queryset.filter(org_id=org_id)
        return queryset

    def get(self, request, id):
        try:
            response_data = []
            employee = Employee.objects.get(id=id)
            if employee.type == "USER":
                empdepartments = EmpDept.objects.filter(emp=id)
                for department in empdepartments:
                    serializer = DepartmentSerializer(department.dept)
                    response_data.append(serializer.data)
                return JsonResponse({"department": response_data}, status=200)

            elif employee.type == "ADMIN":
                org_id = employee.org
                departments = Department.objects.filter(org=org_id)
                for department in departments:
                    serializer = DepartmentSerializer(department)
                    response_data.append(serializer.data)
                return JsonResponse({"department": response_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request):
        try:
            org_id = request.data.get("org")
            org_id_present = Organization.objects.filter(id=org_id).exists()
            if org_id_present:
                pass
                serializer = DepartmentSerializer(
                    data={
                        "name": request.data.get("name"),
                        "org": request.data.get("org"),
                        "employee_count": 0,
                    },
                    partial=True,
                )

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
                return JsonResponse(
                    {"error": "Organization does not exist"}, status=400
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, id):
        try:
            department = Department.objects.get(id=id)
            serializer = DepartmentSerializer(
                department, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Department updated successfully"}, status=200
                )
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=404)

    def delete(self, request, id):
        try:
            department = Department.objects.get(id=id)
            department.delete()
            return Response({"message": "Department deleted successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=404)


class OrganizationAPI(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset().exclude(name="Sakon"))
            serializer = self.get_serializer(queryset, many=True)
            response_data = []
            for d in serializer.data:
                service_provider_ids = [int(id) for id in d["service_providers"]]
                service_providers = ServiceProvider.objects.filter(
                    id__in=service_provider_ids
                )
                service_provider_names = list(
                    service_providers.values_list("name", flat=True)
                )

                response_data.append(
                    {
                        "id": d.get("id"),
                        "name": d.get("name"),
                        "department_count": d.get("department_count"),
                        "service_providers": service_provider_names,
                    }
                )
            return JsonResponse({"data": response_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {
                        "message": "successfully entered data in db",
                        "data": serializer.data,
                    },
                    status=200,
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
                    {
                        "message": "successfully entered data in db",
                        "data": serializer.data,
                    },
                    status=200,
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
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def post(self, request):
        serializer = ServiceProviderSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {
                        "message": "successfully entered data in db",
                        "data": serializer.data,
                    },
                    status=200,
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
                return JsonResponse(
                    {
                        "message": "successfully entered data in db",
                        "data": serializer.data,
                    },
                    status=200,
                )
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


class ConfigurationAPI(generics.ListAPIView):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["$name"]

    @staticmethod
    @api_view(["GET"])
    def getconfigbyid(request, configurationid):
        try:
            queryset = ConfigurationAPI.queryset
            queryset = queryset.filter(id=configurationid)
            serializer = ConfigurationAPI.serializer_class(queryset, many=True)
            response_data = serializer.data
            return JsonResponse({"data": response_data}, status=200)
        except Exception as e:
            return JsonResponse({"message": "internal server error "}, status=404)

    def get(self, request, empid, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            emp = Employee.objects.filter(id=empid)[0]
            if emp.type == "ADMIN":
                org = emp.org.id
                queryset = queryset.filter(org_id=org)
            elif emp.type == "USER":
                department_ids = EmpDept.objects.filter(emp_id=empid).values_list(
                    "dept_id", flat=True
                )
                queryset = queryset.filter(department__in=department_ids)
            scheduled = request.query_params.get("is_scheduled")
            carrier_name = request.query_params.get("carrier_name")
            if scheduled:
                if str(scheduled) == "true":
                    scheduled = True
                else:
                    scheduled = False
                queryset = queryset.filter(is_scheduled=scheduled)
            if carrier_name is not None:
                queryset = queryset.filter(carrier=carrier_name)
            if request.query_params.get("department_id"):
                queryset = queryset.filter(
                    department__id=request.query_params.get("department_id")
                )
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data = serializer.data
                count = self.paginator.page.paginator.count
                previous_url = self.paginator.get_previous_link()
                next_url = self.paginator.get_next_link()

                return self.get_paginated_response(
                    response_data, count, previous_url, next_url
                )

            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

            return JsonResponse({"data": response_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def get_paginated_response(self, data, count, previous_url, next_url):
        try:
            response_data = []
            departments = Department.objects.all()  # get all existing departments
            for d in data:
                department_id = d.get("department")
                # check if the department_id exists in the existing departments
                department = departments.filter(id=department_id).first()
                if department:
                    department_name = department.name
                else:
                    department_name = None
                response_data.append(
                    {
                        "id": d.get("id"),
                        "configurationName": d.get("name"),
                        "department": department_name,
                        "emp": d.get("emp"),
                        "email": d.get("email"),
                        "carrierName": d.get("carrier"),
                        "schedulingStatus": d.get("is_scheduled"),
                        "scheduler_id": d.get("schedule"),
                    }
                )
            return JsonResponse(
                {
                    "count": count,
                    "previous": previous_url,
                    "next": next_url,
                    "data": data,
                    "data": response_data,
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        try:
            empid = request.data.get("emp")
            emp = Employee.objects.filter(id=empid)[0]
            org = emp.org.id
            data = request.data
            data["org"] = org
            serializer = ConfigurationSerializer(data=data)
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
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, configurationid, *args, **kwargs):
        try:
            config = Configuration.objects.get(id=configurationid)
        except Configuration.DoesNotExist:
            return Response({"error": "Invalid Configuration ID"}, status=404)
        serializer = self.get_serializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Configuration updated successfully"})
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

    def delete(self, request, configurationid):
        try:
            configuration = Configuration.objects.get(id=configurationid)
            configuration.delete()
            return JsonResponse({"message": "deleted successfully "}, status=200)
        except Configuration.DoesNotExist:
            return JsonResponse({"error": "Configuration not found"}, status=404)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


class ScheduleAPI(generics.ListAPIView):
    queryset = Schedule.objects.all()
    serializer_class = SchedulerSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["$schedularName"]

    def get(self, request, empid, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(emp_id=empid)
        config = request.query_params.get("config_id")
        if config:
            queryset = queryset.filter(
                Q(configurations__icontains=config) if config else Q(),
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = serializer.data
            count = self.paginator.page.paginator.count
            previous_url = self.paginator.get_previous_link()
            next_url = self.paginator.get_next_link()

            return self.get_paginated_response(
                response_data, count, previous_url, next_url
            )

        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        return JsonResponse({"data": response_data}, status=200)

    def get_paginated_response(self, data, count, previous_url, next_url):
        try:
            response_data = []
            for schedule_data in data:
                schedule_id = schedule_data.get("id")
                schedule = self.queryset.get(id=schedule_id)
                configurations = Configuration.objects.filter(
                    id__in=schedule_data.get("configurations")
                ).values_list("name", flat=True)
                configuration_names = list(configurations)
                if len(configuration_names) != 0:
                    response_data.append(
                        {
                            "id": schedule_data.get("id"),
                            "schedule_name": schedule_data.get("schedularName"),
                            "emp": schedule_data.get("emp"),
                            "configuration": configuration_names,
                            "interval": f"{schedule_data.get('interval')} {schedule_data.get('weekDay') if schedule_data.get('weekDay') is not None else ''} at {schedule_data.get('timeDuration') if schedule_data.get('timeDuration') is not None else ''}",
                            "time": schedule_data.get("timeDuration"),
                            "weekDay": schedule_data.get("weekDay"),
                            "monthDay": schedule_data.get("monthDay"),
                            "timeZone": str(schedule_data.get("timeZone")),
                            "created_at": schedule_data.get("created_at"),
                            "updated_at": schedule_data.get("updated_at"),
                        }
                    )
            return JsonResponse(
                {
                    "count": count,
                    "previous": previous_url,
                    "next": next_url,
                    "data": response_data,
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

    def put(self, request, scheduleid, *args, **kwargs):
        try:
            schedule = Schedule.objects.get(id=scheduleid)
        except Schedule.DoesNotExist:
            return Response({"error": "Invalid Scheduler ID"}, status=404)
        serializer = SchedulerSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            if schedule.configurations != request.data.get("configurations"):
                conf_ids = schedule.configurations
                Configuration.objects.filter(id__in=conf_ids).update(
                    is_scheduled=False, schedule_id=None
                )
                configurations = Configuration.objects.filter(
                    id__in=request.data.get("configurations")
                )
                serializer.save()
                configurations.update(
                    is_scheduled=True, schedule_id=serializer.data.get("id")
                )
            else:
                serializer.save()
            return Response({"message": "Scheduler updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=500)

    def delete(self, request, scheduleid):
        try:
            schedule = Schedule.objects.get(id=scheduleid)
            schedule.delete()
            return JsonResponse(
                {"message": "Schedule deleted successfully "}, status=200
            )
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


class JobsAPI(APIView):
    def get(self, request, empid):
        try:
            jobs = Jobs.objects.filter(emp_id=empid)
            serializer = JobsSerializer(jobs, many=True)
            data = []
            for d in serializer.data:
                configuration = Configuration.objects.get(id=d.get("configuration"))
                schedule = Schedule.objects.get(id=d.get("schedule"))
                department = Department.objects.get(id=d.get("department"))
                data.append(
                    {
                        "id": d.get("id"),
                        "Scheduler_Name": schedule.schedularName,
                        "Configuration_Name": configuration.name,
                        "Department_Name": department.name,
                        "Service": d.get("service"),
                        "Status": d.get("status"),
                        "Triggered_At": d.get("Triggered_At"),
                    }
                )
            return JsonResponse({"data": data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request):
        try:
            serializer = JobsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {
                        "message": "successfully entered data in db",
                        "data": serializer.data,
                    },
                    status=200,
                )
            else:
                return JsonResponse({"error": serializer.errors}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, id):
        try:
            try:
                job = Jobs.objects.get(id=id)
            except Configuration.DoesNotExist:
                return JsonResponse({"message": "Invalid Job id"}, status=404)
            serializer = JobsSerializer(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "Jobs updated successfully"}, status=200
                )
            else:
                return JsonResponse({"error": "Internal Server Error"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, id):
        try:
            try:
                job = Jobs.objects.get(id=id)
                job.delete()
                return JsonResponse(
                    {"message": "Job deleted successfully "}, status=200
                )
            except Jobs.DoesNotExist:
                return JsonResponse({"error": "Job not found"}, status=404)
            except Exception as e:
                return JsonResponse(
                    {
                        "error": "Internal Server Error",
                    },
                    status=500,
                )
        except Exception as e:
            return JsonResponse(
                {
                    "error": str(e),
                },
                status=400,
            )


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

    def delete(self, request, id):
        try:
            download = DownloadReport.objects.get(id=id)
            download.delete()
            return JsonResponse(
                {"message": "Download Report deleted successfully "}, status=200
            )
        except DownloadReport.DoesNotExist:
            return JsonResponse({"error": "Download Report not found"}, status=404)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


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

    def delete(self, request, id):
        try:
            file = FileValidationReport.objects.get(id=id)
            file.delete()
            return JsonResponse(
                {"message": "file validation report deleted successfully "}, status=200
            )
        except FileValidationReport.DoesNotExist:
            return JsonResponse(
                {"error": "file validation report not found"}, status=404
            )
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


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

    def delete(self, request, id):
        try:
            template = TemplateValidationReport.objects.get(id=id)
            template.delete()
            return JsonResponse(
                {"message": "template validation report deleted successfully "},
                status=200,
            )
        except TemplateValidationReport.DoesNotExist:
            return JsonResponse(
                {"error": "template validation report not found"}, status=404
            )
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


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

    def delete(self, request, id):
        try:
            upload = UploadReport.objects.get(id=id)
            upload.delete()
            return JsonResponse(
                {"message": "uplaod report deleted successfully "}, status=200
            )
        except UploadReport.DoesNotExist:
            return JsonResponse({"error": "upload report not found"}, status=404)
        except Exception as e:
            return JsonResponse(
                {
                    "error": "Internal Server Error",
                },
                status=500,
            )


from datetime import datetime


class LoginApi(APIView):
    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            employee = LocalAuth.authenticate(email=email, password=password)
            if employee is not None:
                token = RefreshToken.for_user(employee)
                employeedetails = {}
                employeedetails["id"] = employee.id
                employeedetails["email"] = employee.email
                employeedetails["name"] = employee.name
                employeedetails["type"] = employee.type
                employeedetails["org_id"] = employee.org.id
                employeedetails["org_name"] = employee.org.name
                refresh_payload = jwt.decode(
                    str(token), key=settings.SECRET_KEY, algorithms=["HS256"]
                )
                access_payload = jwt.decode(
                    str(token.access_token),
                    key=settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
                access_exp = datetime.fromtimestamp(access_payload["exp"])
                return Response(
                    {
                        "Message": "Login Successfully",
                        "userdetails": employeedetails,
                        "accesstoken": str(token.access_token),
                        "refreshToken": str(token),
                        "refresh_token_expire": str(refresh_exp),
                        "access_token_expire": str(access_exp),
                    }
                )
            else:
                return Response("Invalide login credentials")
        except Exception as e:
            return Response({"error": str(e)})


class RefreshApi(TokenRefreshView):
    """
    APi for again generating access token from refresh token
    """

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            access_token = response.data.get("access")
            access_payload = jwt.decode(
                str(access_token), key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            access_exp = datetime.datetime.fromtimestamp(access_payload["exp"])
            return Response(
                {
                    "Message": "new Access token generated",
                    "AccessToken": access_token,
                    "access_token_exp": access_exp,
                }
            )

        except Exception as e:
            return Response({"error": str(e)})


class ChartGraphAPI(APIView):
    def get(self, request):
        uploadqueryset = UploadReport.objects.all()
        downloadqueryset = DownloadReport.objects.all()
        jobsqueryset = Jobs.objects.all()
        interval = "monthly"
        if request.query_params:
            org_id = request.query_params.get("organization")
            dept_id = request.query_params.get("department")

            frequency = request.query_params.get("frequency")
            if frequency is not None:
                interval = frequency
            if org_id or dept_id or frequency:
                uploadqueryset = uploadqueryset.filter(
                    Q(organization=org_id) if org_id else Q(),
                    Q(department=dept_id) if dept_id else Q(),
                )
                downloadqueryset = downloadqueryset.filter(
                    Q(organization=org_id) if org_id else Q(),
                    Q(department=dept_id) if dept_id else Q(),
                )
                jobsqueryset = jobsqueryset.filter(
                    Q(organization=org_id) if org_id else Q(),
                    Q(department=dept_id) if dept_id else Q(),
                )
        current_datetime = datetime.now()
        if interval == "daily":
            # Set the start datetime to 24 hours ago
            start_datetime = current_datetime - timedelta(hours=24)
            interval_timedelta = timedelta(hours=2)
        elif interval == "weekly":
            start_datetime = current_datetime - timedelta(days=7)
            interval_timedelta = timedelta(days=1)
        elif interval == "monthly":
            start_datetime = current_datetime - timedelta(days=30)
            interval_timedelta = timedelta(days=1)
        totalUploads = uploadqueryset.filter(Triggered_At__gte=start_datetime).count()
        successuploadcount = uploadqueryset.filter(
            status="Completed", Triggered_At__gte=start_datetime
        ).count()
        failureuploadcount = totalUploads - successuploadcount
        totalDownloads = downloadqueryset.filter(
            Triggered_At__gte=start_datetime
        ).count()
        successdownloadcount = downloadqueryset.filter(
            status="Completed", Triggered_At__gte=start_datetime
        ).count()
        failuredownloadcount = totalDownloads - successdownloadcount

        downloaddata = [
            {"name": "Success", "value": successdownloadcount},
            {"name": "Failure", "value": failuredownloadcount},
        ]
        uploaddata = [
            {"name": "Success", "value": successuploadcount},
            {"name": "Failure", "value": failureuploadcount},
        ]

        error_jobs = jobsqueryset.filter(
            status__in=["Pending", "Failed"], Triggered_At__gte=start_datetime
        )
        error_data = []
        current_interval = start_datetime
        while current_interval < current_datetime:
            error_counts = {}
            if interval == "daily":
                interval_start = current_interval.strftime("%H:00")
                interval_end = (current_interval + interval_timedelta).strftime("%H:00")
                key = f"{interval_start}-{interval_end}"
            elif interval == "weekly":
                key = current_interval.strftime("%A")
            elif interval == "monthly":
                key = current_interval.strftime("%Y-%m-%d")
            errors_within_interval = error_jobs.filter(
                Triggered_At__gte=current_interval,
                Triggered_At__lt=current_interval + interval_timedelta,
            )
            error_counts["name"] = key
            error_counts["error"] = len(errors_within_interval)
            error_data.append(error_counts)
            current_interval += (
                interval_timedelta  # Add this line to increment current_interval
            )
        return JsonResponse(
            {
                "message": "details of graph",
                "downloaddata": downloaddata,
                "uploaddata": uploaddata,
                "errorgraphdata": error_data,
            }
        )


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
                                    args=[
                                        configurations_int,
                                        schedule_id,
                                        schedule.interval,
                                        schedule.emp.id,
                                    ],
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
