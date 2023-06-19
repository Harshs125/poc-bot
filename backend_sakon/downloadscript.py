from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, time, imaplib, email, time, requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Configuration
from .filevalidation import file_validation_check
import requests
from django.views.decorators.csrf import csrf_exempt

def download_file_script(*args):
    print("GEGEGEGEGEGEGE")
    for arg in args[0]:
        config = Configuration.objects.get(id=arg)
        joburl = "http://127.0.0.1:8000/jobs"
        jobdata = {
            "schedule": args[1],
            "configuration": arg,
            "department_name": "DE",
        }
        jobresponse = requests.post(joburl, data=jobdata)
        jobid = jobresponse.json().get("data").get("id")
        downloadurl = f"http://127.0.0.1:8000/jobs/report/download"
        filevalidateurl = f"http://127.0.0.1:8000/jobs/report/filevalidation"
        templatevalideurl = f"http://127.0.0.1:8000/jobs/report/templatevalidation"
        uploadurl = f"http://127.0.0.1:8000/jobs/report/upload"
        reportdata = {"job": jobresponse.json().get("data").get("id")}
        downloadresponse = requests.post(downloadurl, data=reportdata)
        filevalidationresponse = requests.post(filevalidateurl, data=reportdata)
        templatevalidationresponse = requests.post(templatevalideurl, data=reportdata)
        uploadresponse = requests.post(uploadurl, data=reportdata)

        print("download_file_script started")

        chrome_options = Options()
        # prefs = {"download.default_directory" : "Users/adity/OneDrive/Desktop/SAKON_POC_BACKEND/downloaded_files"}
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)

        # Open the verification page in a new browser window
        # configuration.website_url
        driver.get(config.website_url)
        time.sleep(5)

        email_field = driver.find_element("xpath", '//*[@id="email"]')
        # configuration.email
        email_field.send_keys(config.email)

        reg_button = driver.find_element("xpath", "/html/body/form/div/button")
        reg_button.click()

        # Connect to the mail server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(config.email, config.password)
        # check if it actually login

        mail.select("inbox")
        otp_email_address = config.email

        otp = ""
        # Search for the latest email from the sender
        result, data = mail.uid(
            "search", None, f'TO "{otp_email_address}" SUBJECT "OTP"'
        )  # Search for OTP email by sender and subject
        if result == "OK":
            latest_email_uid = data[0].split()[-1]
            result, email_data = mail.uid("fetch", latest_email_uid, "(RFC822)")
            raw_email = email_data[0][1].decode("utf-8")
            email_message = email.message_from_string(raw_email)
            otp = email_message.get_payload()

            mail.logout()

        # Enter the OTP code into the verification field
        otp_field = driver.find_element("xpath", '//*[@id="otp"]')
        otp_field.send_keys(otp)

        # Click the submit button
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="verify"]'))
            )

        except Exception as e:
            print("error:", str(e))

        params = {
            "behavior": "allow",
            "downloadPath": os.path.join(os.getcwd(), "downloaded_files"),
        }
        download_location = params["downloadPath"]

        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

        download_button = driver.find_element("xpath", '//*[@id="download"]')
        filename = download_button.get_attribute("download")
        download_button.click()
        print("The downloaded file is saved in location:", download_location)
        downloadresponse = requests.put(
            f"{downloadurl}/{jobid}",
            data={"status": "Completed", "description": "downloading successfull"},
        )
        # Close the browser window
        # driver.quit()
        # Logout from the mail server
        file_path = f"{download_location}\\{filename}"

        file_validation_check(file_path, jobid, arg, config.sftp_path)
