from django.urls import path

from .views import ClientList, ClientDetail, ContractList, ContractDetail, EventList, EventDetail


app_name = "crm"

urlpatterns = [
    # Clients
    path("clients/", ClientList.as_view(), name="list"),
    path("clients/<int:pk>/", ClientDetail.as_view(), name="detail"),
    # Contracts
    path('contracts/', ContractList.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', ContractDetail.as_view(), name='contract_detail'),
    # Events
    path('events/', EventList.as_view(), name='event_list'),
    path('events/<int:pk>/', EventDetail.as_view(), name='event_detail'),
]
