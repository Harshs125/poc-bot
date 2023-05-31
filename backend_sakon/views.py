
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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os
import pysftp



import time

import imaplib
import email
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

            

import threading
import time
import redis
from pymongo import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os

       

def download_file_script(*args):
    print("download_file_script started")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    # Open the verification page in a new browser window
    # configuration.website_url
    driver.get(args[0].website_url)
    time.sleep(5)


    email_field = driver.find_element("xpath",'//*[@id="email"]')
    # configuration.email
    email_field.send_keys(args[0].email)

    reg_button = driver.find_element("xpath",'/html/body/form/div/button')
    reg_button.click()


    # Connect to the mail server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(args[0].email, args[0].password)
    # check if it actually login

    mail.select('inbox')
    otp_email_address = args[0].email
    
    otp=''
    # Search for the latest email from the sender
    result, data = mail.uid('search', None, f'TO "{otp_email_address}" SUBJECT "OTP"') # Search for OTP email by sender and subject
    if result == 'OK':
        latest_email_uid = data[0].split()[-1]
        result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = email_data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)
        otp = email_message.get_payload()

        mail.logout()
    

    # Enter the OTP code into the verification field
    otp_field = driver.find_element("xpath",'//*[@id="otp"]')
    otp_field.send_keys(otp)

    # Click the submit button
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="verify"]'))
        )
    except TimeoutException:
        print("Element with ID 'verify' not found within the specified wait time.")    

    params={'behavior':'allow','downloadPath':os.getcwd()}


    driver.execute_cdp_cmd('Page.setDownloadBehavior',params)
    

    download_button = driver.find_element("xpath",'//*[@id="download"]')
    download_button.click()

    # Close the browser window
    # driver.quit()

    # Logout from the mail server
    mail.logout()



 # Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['scheduler']
queue = db['job_queue']
 # Set up MongoDBJobStore
jobstore = MongoDBJobStore(collection='jobs', database='scheduler')
 # Set up BackgroundScheduler with MongoDBJobStore
scheduler = BackgroundScheduler(jobstores={'mongo': jobstore})
scheduler.start()
 # Define function to add schedule to MongoDB queue
@csrf_exempt
def add_schedule_to_queue(request, id):
    # Check if schedule_id already exists in the queue
    try:
        if queue.find_one({'schedule_id': id}):
            return JsonResponse({"message": "Schedule already exists in queue."})
        # Add new schedule to the queue
        queue.insert_one({'schedule_id': id})
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
                    schedule_id = next_job['schedule_id']
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
                    if schedule is not None:
                        # Determine cron trigger based on schedule interval and parameters
                        cron_trigger = None
                        if schedule.interval == 'DAILY':
                            cron_trigger = CronTrigger(hour=schedule.time.hour, minute=schedule.time.minute, second=0, timezone=schedule.timeZone)
                        elif schedule.interval == 'WEEKLY':
                            cron_trigger = CronTrigger(day_of_week=schedule.weekDay, hour=schedule.time.hour, minute=schedule.time.minute, second=0, timezone=schedule.timeZone)
                        elif schedule.interval == 'MONTHLY':
                            cron_trigger = CronTrigger(day=schedule.monthDay, hour=schedule.time.hour, minute=schedule.time.minute, second=0, timezone=schedule.timeZone)
                        print(cron_trigger)
                        if cron_trigger is not None :
                            try:
                                configuration = Configuration.objects.get(id=int(schedule.configurations))
                            except Exception as e:
                                print(f"An error occurred: {e}")
                            # configuration = schedule.configurations
                            try:
                                job = scheduler.add_job(download_file_script, trigger=cron_trigger,args=[configuration],  id=str(schedule_id))
                            except Exception as e:
                                print(f"An error occurred: {e}")
                            
                            print(f"Added job: {job}")
                            print("All jobs in scheduler:", scheduler.get_jobs())
                            print(scheduler.get_job(str(schedule_id)))
        except Exception as e:
            print(f"An error occurred: {e}")                    
                    
 # Start BackgroundScheduler in separate thread
 
scheduler_thread = threading.Thread(target=run_scheduler_thread)
@csrf_exempt
def run_thread(request): 
    scheduler_thread.start() 
    return JsonResponse({"message": "Scheduler started."})


            
            
            