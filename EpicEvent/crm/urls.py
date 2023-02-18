from django.urls import path

from .views import ClientList, ClientDetail, ContractList,ContractDetail


app_name = "crm"

urlpatterns = [
    # Clients
    path("clients/", ClientList.as_view(), name="list"),
    path("clients/<int:pk>/", ClientDetail.as_view(), name="detail"),
    # Contracts
    path('contracts/', ContractList.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', ContractDetail.as_view(), name='contract_detail'),
]
