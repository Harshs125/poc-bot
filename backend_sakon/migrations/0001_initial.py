# Generated by Django 4.2 on 2023-06-01 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Carrier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
                ("website_url", models.URLField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Configuration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
                ("dept_name", models.CharField(max_length=250)),
                ("email", models.EmailField(max_length=254)),
                ("password", models.CharField(max_length=250)),
                ("sftp_login", models.CharField(max_length=250)),
                ("sftp_password", models.CharField(max_length=250)),
                ("sftp_path", models.CharField(max_length=500)),
                ("carrier", models.CharField(max_length=250)),
                ("website_url", models.URLField()),
                ("template", models.FileField(upload_to="files/")),
                ("is_scheduled", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=250)),
                ("password", models.CharField(max_length=250)),
                ("type", models.CharField(max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Jobs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("department_name", models.CharField(max_length=250)),
                (
                    "service",
                    models.CharField(
                        choices=[
                            ("Download", "Download"),
                            ("File Validation", "File Validation"),
                            ("Template Validation", "Template Validation"),
                            ("Upload", "Upload"),
                        ],
                        default="Download",
                        max_length=50,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Failed", "Failed"),
                            ("Completed", "Completed"),
                        ],
                        default="Pending",
                        max_length=50,
                    ),
                ),
                ("Triggered_At", models.DateTimeField(auto_now_add=True)),
                (
                    "configuration",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.configuration",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="SuperAdmin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=250)),
                ("password", models.CharField(max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="UploadReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Progress", "Progress"),
                            ("Completed", "Completed"),
                            ("Failed", "Failed"),
                            ("Pending", "Pending"),
                        ],
                        default="Pending",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.CharField(default="Upload is in Pending", max_length=1000),
                ),
                ("attempts", models.IntegerField(default=1)),
                ("Triggered_At", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.jobs",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TemplateValidationReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Progress", "Progress"),
                            ("Completed", "Completed"),
                            ("Failed", "Failed"),
                            ("Pending", "Pending"),
                        ],
                        default="Pending",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default="File validation is in pending", max_length=1000
                    ),
                ),
                ("attempts", models.IntegerField(default=0)),
                ("variance", models.IntegerField(default=0)),
                ("Triggered_At", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.jobs",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("schedularName", models.CharField(max_length=250, unique=True)),
                ("configurations", models.JSONField()),
                (
                    "interval",
                    models.CharField(
                        choices=[("DAILY", 1), ("WEEKLY", 2), ("MONTHLY", 3)],
                        max_length=10,
                    ),
                ),
                ("timeDuration", models.TimeField()),
                ("weekDay", models.CharField(max_length=250, null=True)),
                ("monthDay", models.IntegerField(null=True)),
                ("timeZone", models.CharField(default="UTC", max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "emp",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.employee",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="jobs",
            name="schedule",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend_sakon.schedule",
            ),
        ),
        migrations.CreateModel(
            name="FileValidationReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Progress", "Progress"),
                            ("Completed", "Completed"),
                            ("Failed", "Failed"),
                            ("Pending", "Pending"),
                        ],
                        default="Pending",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default="File validation is in pending", max_length=1000
                    ),
                ),
                ("attempts", models.IntegerField(default=0)),
                ("Triggered_At", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.jobs",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FileMetaData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250, unique=True)),
                ("size", models.IntegerField()),
                ("type", models.CharField(max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "config",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.configuration",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="employee",
            name="org",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend_sakon.organization",
            ),
        ),
        migrations.CreateModel(
            name="DownloadReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Progress", "Progress"),
                            ("Completed", "Completed"),
                            ("Failed", "Failed"),
                            ("Pending", "Pending"),
                        ],
                        default="Progress",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default="download is in progress", max_length=1000
                    ),
                ),
                ("attempts", models.IntegerField(default=1)),
                ("Triggered_At", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.jobs",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250)),
                (
                    "org",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.organization",
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "org_id")},
            },
        ),
        migrations.AddField(
            model_name="configuration",
            name="emp",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend_sakon.employee",
            ),
        ),
        migrations.AddField(
            model_name="configuration",
            name="schedule",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="backend_sakon.schedule",
            ),
        ),
        migrations.CreateModel(
            name="EmpDept",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "dept",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.department",
                    ),
                ),
                (
                    "emp",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.employee",
                    ),
                ),
            ],
            options={
                "unique_together": {("dept_id", "emp_id")},
            },
        ),
        migrations.CreateModel(
            name="AdminOrganization",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "admin",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.employee",
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="backend_sakon.organization",
                    ),
                ),
            ],
            options={
                "unique_together": {("admin_id", "org_id")},
            },
        ),
    ]
