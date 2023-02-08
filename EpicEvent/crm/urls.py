from django.urls import path, include
from rest_framework.routers import DefaultRouter


client_router = DefaultRouter()


urlpatterns = [
    path('', include(client_router.urls)),
]