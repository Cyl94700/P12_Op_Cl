from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('crm/', include('crm.urls')),

]
admin.site.site_header = "EpicEvents Admin"
admin.site.site_title = "EpicEvents Admin"
admin.site.index_title = "EpicEvents Admin"
