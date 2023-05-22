from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    ConfigurationSerializer,
    SchedulerSerializer,
    EmployeesSerializer,
    OragnizationSerializer,
)
from .models import Organization, Employee, Configuration, Schedule


class EmployeesAPI(APIView):
    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        if id is not None:
            employees = Employee.objects.get(id=id)
            serializer = EmployeesSerializer(employees)
        else:
            employees = Employee.objects.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(employees, request)
            serializer = EmployeesSerializer(result_page, many=True)
        return JsonResponse(
            {
                "count": paginator.page.paginator.count,
                "previous": paginator.get_previous_link(),
                "next": paginator.get_next_link(),
                "data": serializer.data,
            },
            status=200,
        )

    def post(self, request):
        serializer = EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "successfully entered data in db"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class OrganizationAPI(APIView):
    pagination_class = PageNumberPagination

    def get(self, request, id=None):
        if id is not None:
            organization = Organization.objects.get(id=id)
            serializer = OragnizationSerializer(organization)
        else:
            organization = Organization.objects.all()
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(organization, request)
            serializer = OragnizationSerializer(result_page, many=True)
        return JsonResponse(
            {
                "count": paginator.page.paginator.count,
                "previous": paginator.get_previous_link(),
                "next": paginator.get_next_link(),
                "data": serializer.data,
            },
            status=200,
        )

    def post(self, request):
        serializer = EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "successfully entered data in db"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class ConfigurationAPI(APIView):
    pagination_class = PageNumberPagination
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def get_serializer(self, *args, **kwargs):
        return ConfigurationSerializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            dept_name = request.query_params.get("dept_name")
            is_scheduled = request.query_params.get("is_scheduled")
            configurations = Configuration.objects.filter(
                Q(dept_name=dept_name) if dept_name else Q(),
                Q(is_scheduled=is_scheduled) if is_scheduled is not None else Q(),
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
            return JsonResponse({"error": str(e)}, status=400)

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
            return JsonResponse({"error": str(e)}, status=400)

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
                if len(configuration_names) is not 0:
                    data.append(
                        {
                            "id": schedule.id,
                            "schedule_name": schedule.schedularName,
                            "emp": schedule.emp.id,
                            "configuration": configuration_names,
                            "interval": str(
                                schedule.interval
                                + " "
                                + schedule.weekDay
                                + " "
                                + "at "
                                + str(schedule.time)
                            ),
                            "time": schedule.time,
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
            return JsonResponse({"error": str(e)}, status=400)

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
