from django.urls import path


from .views import ClientList, ClientDetail


app_name = "crm"

urlpatterns = [
    path("", ClientList.as_view(), name="list"),
    path("<int:pk>/", ClientDetail.as_view(), name="detail"),
]
