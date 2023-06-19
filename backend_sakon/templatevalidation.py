import requests, os, csv
from .fileupload import upload_file_to_sftp
from .models import Configuration


def template_validation_check(filepath, config_id, jobid, sftp_path):
    config = Configuration.objects.filter(id=config_id)[0]
    templatepath = str(config.template)
    if os.path.exists(templatepath):
        print("Template path is valid")
    else:
        print("Template path is not valid")

    response = requests.put(
        f"http://127.0.0.1:8000/jobs/{jobid}",
        data={"service": "Template Validation", "status": "Pending"},
    )
    if validate(filepath, templatepath, jobid):
        print("Template validation successfull")
        templatedvalidationurl = (
            f"http://127.0.0.1:8000/jobs/report/templatevalidation/{jobid}"
        )
        response = requests.put(
            templatedvalidationurl,
            data={
                "status": "Completed",
                "description": "Template Validation is successfull",
                "attempts": 1,
            },
        )
        upload_file_to_sftp(filepath, jobid, sftp_path)

    else:
        response = requests.put(
            f"http://127.0.0.1:8000/jobs/report/templatevalidation{jobid}",
            data={"service": "Template Validation", "status": "Failed", "attempts": 1},
        )
        response = requests.put(
            f"http://127.0.0.1:8000/jobs/{jobid}",
            data={"service": "Template Validation", "status": "Failed", "attempst": 1},
        )
        print("Template validation unsuccessfull")


def validate(filepath, templatepath, jobid):
    header_weight = 4
    row_weight = 3
    column_match_weight = 2
    column_diff_weight = 1

    with open(filepath, "r") as file_csv:
        file_reader = csv.reader(file_csv)
        file_headers = next(file_reader)
        file_record_count = sum(1 for _ in file_reader)
        file_records = list(file_reader)

    with open(templatepath, "r") as template_csv:
        template_reader = csv.reader(template_csv)
        template_headers = next(template_reader)
        template_record_count = sum(1 for _ in template_reader)
        template_records = list(template_reader)
    if file_headers != template_headers:
        variance = (
            header_weight * int(file_headers != template_headers)
            + row_weight * abs(len(file_records) - len(template_records))
            + column_match_weight * abs(len(file_headers) - len(template_headers))
            + column_diff_weight * (len(file_headers) != len(template_headers))
        )
        error = "Headers do not match:"
        print("Headers do not match:")
        print(
            "Missing headers in target file:", set(file_headers) - set(template_headers)
        )
        print(
            "Extra headers in target file:", set(template_headers) - set(file_headers)
        )
        templatedvalidationurl = f"http://127.0.0.1:8000/jobs/report/template/{jobid}"
        response = requests.put(
            templatedvalidationurl,
            data={"status": "Failed", "description": error, "attempts": 1},
        )
        return False
    if file_record_count != template_record_count:
        variance = (
            header_weight * int(file_headers != template_headers)
            + row_weight * abs(len(file_records) - len(template_records))
            + column_match_weight * abs(len(file_headers) - len(template_headers))
            + column_diff_weight * (len(file_headers) != len(template_headers))
        )
        error = "Record count does not match:"
        print("Record count does not match:")
        templatedvalidationurl = f"http://127.0.0.1:8000/jobs/report/template/{jobid}"
        response = requests.put(
            templatedvalidationurl,
            data={"status": "Failed", "description": error, "attempts": 1},
        )
        return False
    return True
