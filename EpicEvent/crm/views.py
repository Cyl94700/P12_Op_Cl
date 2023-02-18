from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import SALES, SUPPORT
from .models import Client, Contract
from .permissions import ClientPermissions, ContractPermissions, IsManager
from .serializers import ClientSerializer, ContractSerializer


class ClientList(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsManager | ClientPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["last_name", "email", "company_name"]
    # filterset_fields = ["last_name", "email", "company_name"]
    filterset_fields = ["sales_contact"]

    def get_queryset(self):
        if self.request.user.team.name == SUPPORT:
            return Client.objects.filter(
                contract__event__support_contact=self.request.user
            ).distinct()
        elif self.request.user.team.name == SALES:
            null_clients = Client.objects.filter(sales_contact__isnull=True)
            own_clients = Client.objects.filter(sales_contact=self.request.user)
            return null_clients | own_clients
        return Client.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    http_method_names = ["get", "put", "delete", "options"]
    permission_classes = [IsAuthenticated, IsManager | ClientPermissions]
    serializer_class = ClientSerializer

    def update(self, request, *args, **kwargs):
        client = self.get_object()
        serializer = ClientSerializer(data=request.data, instance=client)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class ContractList(generics.ListCreateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, IsManager | ContractPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "client__last_name",
        "client__email",
        "client__company_name",
    ]
    filterset_fields = {
        "datetime_created": ["gte", "lte"],
        "payment_due": ["gte", "lte"],
        "amount": ["gte", "lte"],
        "status_sign": ["exact"],
    }

    def get_queryset(self):
        if self.request.user.team.name == SUPPORT:
            return Contract.objects.filter(event__support_contact=self.request.user)
        elif self.request.user.team.name == SALES:
            return Contract.objects.filter(sales_contact=self.request.user)
        return Contract.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = ContractSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["sales_contact"] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContractDetail(generics.RetrieveUpdateAPIView):
    queryset = Contract.objects.all()
    http_method_names = ["get", "put", "options"]
    permission_classes = [IsAuthenticated, IsManager | ContractPermissions]
    serializer_class = ContractSerializer

    def update(self, request, *args, **kwargs):
        serializer = ContractSerializer(data=request.data, instance=self.get_object())
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["sales_contact"] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
