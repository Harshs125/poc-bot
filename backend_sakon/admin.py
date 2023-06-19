from django.contrib import admin
from .models import *

admin.site.register(Organization)
admin.site.register(Employee)
admin.site.register(Department)
admin.site.register(EmpDept)
admin.site.register(Configuration)
admin.site.register(Schedule)
admin.site.register(DownloadReport)
admin.site.register(FileValidationReport)
admin.site.register(TemplateValidationReport)
admin.site.register(UploadReport)
admin.site.register(Jobs)
admin.site.register(ServiceProvider)
admin.site.register(SignUpInfo)
