from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import SALES, SUPPORT
from .models import Client
from .permissions import ClientPermissions, IsManager
from .serializers import ClientSerializer


class ClientList(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsManager | ClientPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "email"]
    filterset_fields = ["first_name", 'last_name', 'email']

    def get_queryset(self):
        if self.request.user.team.name == SUPPORT:
            return Client.objects.filter(
                contract__event__support_contact=self.request.user
            ).distinct()
        elif self.request.user.team.name == SALES:
            all_clients = Client.objects.filter(sales_contact="")
            own_clients = Client.objects.filter(sales_contact=self.request.user)
            return all_clients | own_clients
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
