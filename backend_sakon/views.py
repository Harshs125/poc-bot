
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import threading
import time
from pymongo import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
import csv
import statistics
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics
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
    DepartmentSerialzer,
    JobsSerializer,
    DownloadSerializer,
    FileValidatorSerializer,
    UploadValidatorSerializer,
    TemplateValidatorSerializer
)
import json
import requests
from .models import Organization, Employee, Configuration, Schedule, Department, Jobs, DownloadReport,FileValidationReport,UploadReport,TemplateValidationReport

client = MongoClient('mongodb://localhost:27017/')
db = client['scheduler']
queue = db['job_queue']
 # Set up MongoDBJobStore
jobstore = MongoDBJobStore(collection='jobs', database='scheduler')
 # Set up BackgroundScheduler with MongoDBJobStore
scheduler = BackgroundScheduler(jobstores={'mongo': jobstore})
scheduler.start()




class EmployeesAPI(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeesSerializer
    pagination_class = PageNumberPagination

    def post(self, request):
        serializer = EmployeesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "successfully entered data in db"}, status=200
            )
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class OrganizationAPI(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OragnizationSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        org_id = self.kwargs.get("id")
        if org_id:
            return Organization.objects.filter(id=org_id)
        return Organization.objects.all()

    def post(self, request):
        serializer = OragnizationSerializer(data=request.data)
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
            scheduled = request.query_params.get("is_scheduled")
            if scheduled is not None:
                if str(scheduled)=="true":
                    scheduled=True
                else:
                    scheduled=False
            carrier_name=request.query_params.get("carrier_name")
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
                    print("----?????",data)
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
                    queue.insert_one({"schedule_id":serializer.data.get("id")})
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


class DepartmentAPI(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerialzer
    pagination_class = PageNumberPagination


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
                {"message": "successfully entered data in db","data":serializer.data}, status=200
            )
        else:
            return JsonResponse({"error": serializer.errors}, status=400)

    def put(self,request, id):
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
    def get(self,request,jobid):
        try:
            download=DownloadReport.objects.filter(job=jobid)
        except DownloadReport.DoesNotExist:
            return JsonResponse({"message":"Invalid job id"},status=400)
        serializer = DownloadSerializer(download,many=True)
        return JsonResponse({"message":"success","data":serializer.data},status=200)
    def post(self,request):
        serializer=DownloadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"created download"},status=200)
        else:
            return JsonResponse({"error":"Internal Server Error"},status=400)
        
    def put(self,request,jobid):
        try:
            donwload = DownloadReport.objects.get(job=jobid)
        except DownloadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = DownloadSerializer(donwload, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Download report updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

class FileValidatorAPI(APIView):
    def get(self,request,jobid):
        try:
            filevalidate=FileValidationReport.objects.filter(job=jobid)
        except FileValidationReport.DoesNotExist:
            return JsonResponse({"message":"Invalid job id"},status=400)
        serializer=FileValidatorSerializer(filevalidate,many=True)
        return JsonResponse({"message":"success","data":serializer.data},status=200)
    def post(self,request):
        serializer=FileValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"created FileValidation report"},status=200)
        else:
            return JsonResponse({"error":"Internal Server Error"},status=400)
    def put(self,request,jobid):
        try:
            filevalidate = FileValidationReport.objects.get(job=jobid)
        except FileValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = FileValidatorSerializer(filevalidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Filevalidation report updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)

class TemplateValidatorAPI(APIView):
    def get(self,request,jobid):
        try:
            templatevalidate=TemplateValidationReport.objects.filter(job=jobid)
        except TemplateValidationReport.DoesNotExist:
            return JsonResponse({"message":"Invalid job id"},status=400)
        serializer = TemplateValidatorSerializer(templatevalidate,many=True)
        return JsonResponse({"message":"success","data":serializer.data},status=200)
    def post(self,request):
        serializer=TemplateValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"created TemplateValidation report"},status=200)
        else:
            return JsonResponse({"error":"Internal Server Error"},status=400)
    def put(self,request,jobid):
        try:
            templatevalidate = TemplateValidationReport.objects.get(job=jobid)
        except TemplateValidationReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = TemplateValidatorSerializer(templatevalidate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Templatevalidation report updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)


class UploadValidatorAPI(APIView):
    def get(self,request,jobid):
        try:
            uploadreport=UploadReport.objects.filter(job=jobid)
        except UploadReport.DoesNotExist:
            return JsonResponse({"message":"Invalid job id"},status=400)
        serializer = UploadValidatorSerializer(uploadreport,many=True)
        return JsonResponse({"message":"success","data":serializer.data},status=200)
    def post(self,request):
        serializer=UploadValidatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"created Upload report"},status=200)
        else:
            return JsonResponse({"error":"Internal Server Error"},status=400)
    def put(self,request,jobid):
        try:
            upload = UploadReport.objects.get(job=jobid)
        except UploadReport.DoesNotExist:
            return JsonResponse({"message": "Invalid Job id"}, status=404)
        serializer = UploadValidatorSerializer(upload, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message": "Upload report updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Internal Server Error"}, status=400)





 
 

def upload_file_to_sftp(filepath,jobid):
    
    sftpHost = 'localhost'
    sftpPort = 22
    uname = 'adity'
    privateKeyFilePath = './id_rsa'

    cnOpts = pysftp.CnOpts()
    cnOpts.hostkeys = None
    response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
        "service":"Upload",
        "status":"Pending",
    })
    # Create an SFTP connection
    uploadvalidationurl=f"http://127.0.0.1:8000/jobs/report/upload/{jobid}"
    
    with pysftp.Connection(host=sftpHost, port=sftpPort, username=uname, private_key=privateKeyFilePath, cnopts=cnOpts) as sftp:
        # Upload file to SFTP server
        local_filepath = filepath  # Assuming the file is uploaded via a form with a file field
        filename = os.path.basename(local_filepath)
        remote_filepath = f'C:/Users/adity/Sakon files/{filename}'  # Replace with the remote filepath where you want to store the file on the SFTP server
        try:
            sftp.put(local_filepath, remote_filepath)
        except Exception as e:
            print("File uploaded unsuccessfully")
            response=requests.put(uploadvalidationurl,data={
            "status":"Failed",
            "description":str(e),
            "attempts":1
            }) 
            response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
            "service":"Upload",
            "status":"Failed",
            "attempts":1
            })
        finally:
            response=requests.put(uploadvalidationurl,data={
            "status":"Completed",
            "description":"Upload to sftp successfully",
            "attempts":1
            })
            response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
            "service":"Upload",
            "status":"Completed",
            "attempts":1
            })


def validate(filepath,templatepath,jobid):
    header_weight = 4
    row_weight = 3
    column_match_weight = 2
    column_diff_weight = 1

    with open(filepath, 'r') as file_csv:
        file_reader = csv.reader(file_csv)
        file_headers = next(file_reader)
        file_record_count = sum(1 for _ in file_reader)
        file_records=list(file_reader)

    with open(templatepath, 'r') as template_csv:
        template_reader = csv.reader(template_csv)
        template_headers = next(template_reader)
        template_record_count = sum(1 for _ in template_reader)
        template_records=list(template_reader)
    if file_headers != template_headers:
        variance = (header_weight * int(file_headers != template_headers) +
                row_weight * abs(len(file_records) - len(template_records)) +
                column_match_weight * abs(len(file_headers) - len(template_headers)) +
                column_diff_weight * (len(file_headers) != len(template_headers)))
        error="Headers do not match:"
        print("Headers do not match:")
        print("Missing headers in target file:", set(file_headers) - set(template_headers))
        print("Extra headers in target file:", set(template_headers) - set(file_headers))
        print(variance)
        templatedvalidationurl=f"http://127.0.0.1:8000/jobs/report/template/{jobid}"
        response=requests.put(templatedvalidationurl,data={
            "status":"Failed",
            "description":error,
            "attempts":1
        })
        return False
    if file_record_count != template_record_count:
        variance = (header_weight * int(file_headers != template_headers) +
                row_weight * abs(len(file_records) - len(template_records)) +
                column_match_weight * abs(len(file_headers) - len(template_headers)) +
                column_diff_weight * (len(file_headers) != len(template_headers)))
        error="Record count does not match:"
        print("Record count does not match:")
        print("Difference in record count:", abs(file_record_count - template_record_count))
        print(variance)
        templatedvalidationurl=f"http://127.0.0.1:8000/jobs/report/template/{jobid}"
        response=requests.put(templatedvalidationurl,data={
            "status":"Failed",
            "description":error,
            "attempts":1
        })
        return False
    return True


def template_valid_check(filepath,config_id,jobid):
    config=Configuration.objects.filter(id=config_id)[0]
    templatepath=str(config.template)
    #templatepath=r"C:\Users\adity\OneDrive\Desktop\SAKON_POC_BACKEND\files\simulated_call_centre.csv"
    if os.path.exists(templatepath):
        print("Template path is valid")
    else:
        print("Template path is not valid")
        
    response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
        "service":"Template Validation",
        "status":"Pending"
    })
    if validate(filepath,templatepath,jobid):
        print("Template validation successfull")
        templatedvalidationurl=f"http://127.0.0.1:8000/jobs/report/templatevalidation/{jobid}"
        response=requests.put(templatedvalidationurl,data={
            "status":"Completed",
            "description":"Template Validation is successfull",
            "attempts":1
        })
        print(response.json())
        upload_file_to_sftp(filepath,jobid)
    else:
        response=requests.put(f"http://127.0.0.1:8000/jobs/report/templatevalidation{jobid}",data={
        "service":"Template Validation",
        "status":"Failed",
        "attempts":1
         })
        response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
        "service":"Template Validation",
        "status":"Failed",
        "attempst":1
         })
        print("Template validation unsuccessfull")    
    
    
columns=['date','call_started','call_answered','call_ended','service_length','wait_length']
def is_valid(filepath):
    ext= os.path.splitext(filepath)[1]
    if ext.lower() != ".csv":
        print("not csv file")
        return False
    with open(filepath, 'r') as file :
        reader=csv.reader(file)
        header = next(reader)
        count=sum(1 for row in reader)
        if count==0:
            return False
        if not set(columns).issubset(header):
            return False

    return True


def is_valid_check(filepath,jobid,config_id):
    response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
        "service":"File Validation",
        "status":"Pending"
    })
    filevalidationurl=f"http://127.0.0.1:8000/jobs/report/filevalidation/{jobid}"
    filevalidationresponse=requests.put(filevalidationurl,data={
        "status":"Progress",
        "description":"File Validation is in progress",
        "attempts":1
    })
    if is_valid(filepath):
        print("the file is valid")
        filevalidationresponse=requests.put(filevalidationurl,data={
        "status":"Completed",
        "description":"File Validation is Completed",
        "attempt":1
        })
        template_valid_check(filepath,config_id,jobid)
    
    else:
        filevalidationresponse=requests.put(filevalidationurl,data={
        "status":"Failed",
        "description":"File Validation is not successfull",
        "attempts":1
        })
        response=requests.put(f"http://127.0.0.1:8000/jobs/{jobid}",data={
        "service":"File Validation",
        "status":"Failed",
        "attempts":1
         })
        print("the file is not valid")
        
       

def download_file_script(*args):
    for arg in args[0]:
        config = Configuration.objects.get(id=arg)
        joburl='http://127.0.0.1:8000/jobs'
        jobdata={
            'schedule':args[1],
            'configuration':arg,
            'department_name':"DE",
        }
        jobresponse=requests.post(joburl,data=jobdata)
        jobid=jobresponse.json().get('data').get('id')
        print("--->>>>>>>",jobresponse.json().get('data').get('id'))
        downloadurl=f"http://127.0.0.1:8000/jobs/report/download"
        filevalidateurl=f"http://127.0.0.1:8000/jobs/report/filevalidation"
        templatevalideurl=f"http://127.0.0.1:8000/jobs/report/templatevalidation"
        uploadurl=f"http://127.0.0.1:8000/jobs/report/upload"
        reportdata={
            "job":jobresponse.json().get('data').get('id')
        }
        print("------>>>>>>>>>",downloadurl)
        downloadresponse=requests.post(downloadurl,data=reportdata)
        filevalidationresponse=requests.post(filevalidateurl,data=reportdata)
        templatevalidationresponse=requests.post(templatevalideurl,data=reportdata)
        uploadresponse=requests.post(uploadurl,data=reportdata)
        
        print("download_file_script started")
        
        chrome_options = Options()
        # prefs = {"download.default_directory" : "Users/adity/OneDrive/Desktop/SAKON_POC_BACKEND/downloaded_files"}
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)

        # Open the verification page in a new browser window
        # configuration.website_url
        driver.get(config.website_url)
        time.sleep(5)


        email_field = driver.find_element("xpath",'//*[@id="email"]')
        # configuration.email
        email_field.send_keys(config.email)

        reg_button = driver.find_element("xpath",'/html/body/form/div/button')
        reg_button.click()


        # Connect to the mail server
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(config.email, config.password)
        # check if it actually login

        mail.select('inbox')
        otp_email_address = config.email
        
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
        
        except Exception as e:
            
            print("error:",str(e))
            
            
        params={'behavior':'allow','downloadPath':os.path.join(os.getcwd(),'downloaded_files')}
        download_location = params['downloadPath']



        driver.execute_cdp_cmd('Page.setDownloadBehavior',params)
        

        download_button = driver.find_element("xpath",'//*[@id="download"]')
        filename = download_button.get_attribute("download") 
        download_button.click()
        print("The downloaded file is saved in location:", download_location)
        downloadresponse=requests.put(f"{downloadurl}/{jobid}",data={
            "status":"Completed",
            "description":"downloading successfull"
        })
        # Close the browser window
        # driver.quit()
        # Logout from the mail server
        file_path=f"{download_location}\\{filename}"
        
        print("------------------>>>>>",file_path)
        
        is_valid_check(file_path,jobid,arg)
        
 # Set up MongoDB connection
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

                    configurations_int = []
                    configurations_list = schedule.configurations
                    for config in configurations_list:
                        configurations_int.append(int(config))
                    
                    
                    if schedule is not None:
                        # Determine cron trigger based on schedule interval and parameters
                        cron_trigger = None
                        if schedule.interval == 'DAILY':
                            cron_trigger = CronTrigger(hour=schedule.timeDuration.hour, minute=schedule.timeDuration.minute, second=0, timezone=schedule.timeZone)
                        elif schedule.interval == 'WEEKLY':
                            cron_trigger = CronTrigger(day_of_week=schedule.weekDay, hour=schedule.timeDuration.hour, minute=schedule.timeDuration.minute, second=0, timezone=schedule.timeZone)
                        elif schedule.interval == 'MONTHLY':
                            cron_trigger = CronTrigger(day=schedule.monthDay, hour=schedule.timeDuration.hour, minute=schedule.timeDuration.minute, second=0, timezone=schedule.timeZone)
                        print(cron_trigger)
                        if cron_trigger is not None :
                            
                            # configuration = schedule.configurations
                            try:
                                job = scheduler.add_job(download_file_script, trigger=cron_trigger,args=[configurations_int,schedule_id],  id=str(schedule_id))
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                # Push the schedule ID back into the queue
                                queue.insert_one({"schedule_id": schedule_id})
                                print(f"Schedule ID {schedule_id} pushed back into the queue")
                            
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
    
