from .models import APIConfig, GeneratedURL, WebsiteData, CompanyURL, PostedWebsite,TaskInfo, OpenAI_APIKeyConfig, SiteRecordContentGen
from django.contrib import admin


class APIConfigAdmin(admin.ModelAdmin):
    list_display = ('website', 'user', 'password', 'template_no', 'site_enable') 


@admin.register(CompanyURL)
class CompanyURLAdmin(admin.ModelAdmin):
    search_fields = ['generated_url', 'company_website']

admin.site.register(APIConfig, APIConfigAdmin)
admin.site.register(OpenAI_APIKeyConfig)
admin.site.register(GeneratedURL)
admin.site.register(WebsiteData)
admin.site.register(SiteRecordContentGen)
admin.site.register(PostedWebsite)
admin.site.register(TaskInfo)