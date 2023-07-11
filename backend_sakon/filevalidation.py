import requests, csv, os
from .templatevalidation import template_validation_check

columns = [
    "date",
    "call_started",
    "call_answered",
    "call_ended",
    "service_length",
    "wait_length",
]


def file_validation_check(filepath, jobid, config_id, sftp_path):
    response = requests.put(
        f"http://127.0.0.1:8000/jobs/{jobid}",
        data={"service": "File Validation", "status": "Pending"},
    )
    filevalidationurl = f"http://127.0.0.1:8000/jobs/report/filevalidation/{jobid}"
    filevalidationresponse = requests.put(
        filevalidationurl,
        data={
            "status": "Progress",
            "description": "File Validation is in progress",
            "attempts": 1,
        },
    )
    if isvalid(filepath):
        print("the file is valid")
        filevalidationresponse = requests.put(
            filevalidationurl,
            data={
                "status": "Completed",
                "description": "File Validation is Completed",
                "attempt": 1,
            },
        )
        template_validation_check(filepath, config_id, jobid, sftp_path)

    else:
        filevalidationresponse = requests.put(
            filevalidationurl,
            data={
                "status": "Failed",
                "description": "File Validation is not successfull",
                "attempts": 1,
            },
        )
        response = requests.put(
            f"http://127.0.0.1:8000/jobs/{jobid}",
            data={"service": "File Validation", "status": "Failed", "attempts": 1},
        )
        print("the file is not valid")


def isvalid(filepath):
    ext = os.path.splitext(filepath)[1]
    if ext.lower() != ".csv":
        print("not csv file")
        return False
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        count = sum(1 for row in reader)
        if count == 0:
            return False
        if not set(columns).issubset(header):
            return False

    return True
