from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(SuperAdmin)
admin.site.register(Organization)
admin.site.register(Employee)
admin.site.register(AdminOrganization)
admin.site.register(Department)
admin.site.register(EmpDept)
admin.site.register(Configuration)
admin.site.register(FileMetaData)
admin.site.register(Schedule)