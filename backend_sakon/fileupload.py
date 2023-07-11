import requests, pysftp, os


def upload_file_to_sftp(filepath, jobid, sftp_path):
    sftpHost = "localhost"
    sftpPort = 22
    uname = "adity"
    privateKeyFilePath = "./id_rsa"

    cnOpts = pysftp.CnOpts()
    cnOpts.hostkeys = None
    response = requests.put(
        f"http://127.0.0.1:8000/jobs/{jobid}",
        data={
            "service": "Upload",
            "status": "Pending",
        },
    )
    # Create an SFTP connection
    uploadvalidationurl = f"http://127.0.0.1:8000/jobs/report/upload/{jobid}"

    with pysftp.Connection(
        host=sftpHost,
        port=sftpPort,
        username=uname,
        private_key=privateKeyFilePath,
        cnopts=cnOpts,
    ) as sftp:
        # Upload file to SFTP server
        local_filepath = (
            filepath  # Assuming the file is uploaded via a form with a file field
        )
        filename = os.path.basename(local_filepath)
        # remote_filepath = f"C:/Users/adity/Sakon files/{filename}"
        # Replace with the remote filepath where you want to store the file on the SFTP server
        remote_filepath = f"{sftp_path}\\{filename}"
        try:
            sftp.put(local_filepath, remote_filepath)
        except Exception as e:
            print("File uploaded unsuccessfully")
            response = requests.put(
                uploadvalidationurl,
                data={"status": "Failed", "description": str(e), "attempts": 1},
            )
            response = requests.put(
                f"http://127.0.0.1:8000/jobs/{jobid}",
                data={"service": "Upload", "status": "Failed", "attempts": 1},
            )
        finally:
            response = requests.put(
                uploadvalidationurl,
                data={
                    "status": "Completed",
                    "description": "Upload to sftp successfully",
                    "attempts": 1,
                },
            )
            response = requests.put(
                f"http://127.0.0.1:8000/jobs/{jobid}",
                data={"service": "Upload", "status": "Completed", "attempts": 1},
            )
