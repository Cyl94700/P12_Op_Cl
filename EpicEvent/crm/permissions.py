from rest_framework import permissions

from users.models import SALES, SUPPORT, MANAGEMENT
from .models import Client


class ClientPermissions(permissions.BasePermission):
    """
    Sales team :
    Crée des nouveaux clients
    Visualise et modifie les nouveaux clients et ses propres clients
    Peut effacer un client sans contrats
    Support team :
    Visualise ses propres clients
    """

    def has_permission(self, request, view):
        if request.user.team.name == SUPPORT:
            return request.method in permissions.SAFE_METHODS
        return request.user.team.name == SALES

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.team.name == SALES
        elif request.method == "PUT":
            return request.user.team.name == SALES
        elif (
            request.user.team.name == SUPPORT
            and request.method in permissions.SAFE_METHODS
        ):
            return obj in Client.objects.filter(
                contract__event__support_contact=request.user
            )
        return request.user == obj.sales_contact


class IsManager(permissions.BasePermission):
    """
    Managers :
    Peuvent seulement visualiser le CRM
    Mais ils peuvent Créer, modifier ou effacer via le site d'administration
    """

    def has_permission(self, request, view):
        return (
            request.user.team.name == MANAGEMENT
            and request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
