from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from users.models import SALES, SUPPORT, MANAGEMENT
from .models import Client, Contract


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
            return request.user.team.name == SALES and request.user == obj.sales_contact
        elif request.method == "PUT":
            return request.user.team.name == SALES and request.user == obj.sales_contact
        elif (
            request.user.team.name == SUPPORT
            and request.method in permissions.SAFE_METHODS
        ):
            return obj in Client.objects.filter(
                contract__event__support_contact=request.user
            )
        return request.user == obj.sales_contact


class ContractPermissions(permissions.BasePermission):
    """
    Sales team :
    Crée des nouveaux contrats et peut les visualiser ou les modifier s'ils ne sont pas signés.
    Support team :
    Ne peut que visualiser les contrats de ses propres clients
    """

    def has_permission(self, request, view):
        if request.user.team.name == SUPPORT:
            return request.method in permissions.SAFE_METHODS
        return request.user.team.name == SALES

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.team.name == SUPPORT:
                return obj in Contract.objects.filter(
                    event__support_contact=request.user
                )
            return request.user == obj.sales_contact
        elif request.method == "PUT" and obj.status_sign is True:
            raise PermissionDenied("Not permited to update a signed contract.")
        return request.user == obj.sales_contact and obj.status_sign is False


class EventPermissions(permissions.BasePermission):
    """
    Sales team :
    Un vendeur voit et modifie ses propres événements tant qu'ils ne sont pas terminés
    Support team :
    Visulalise et modifie ses propres événements tant qu'ils ne sont pas terminés.
    """

    def has_permission(self, request, view):
        if request.user.team.name == SUPPORT:
            return request.method in ["GET", "PUT"]
        return request.user.team.name == SALES

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (request.user == obj.support_contact
                    or request.user == obj.contract.sales_contact)
        else:
            if obj.status is True:
                raise PermissionDenied("Not permited to update a finished event.")
            if request.user.team.name == SUPPORT:
                return request.user == obj.support_contact
            return request.user == obj.contract.sales_contact


class IsManager(permissions.BasePermission):
    """
    Managers :
    Peuvent seulement visualiser le CRM
    Mais ils peuvent créer, modifier ou effacer via le site d'administration
    """

    def has_permission(self, request, view):
        return (request.user.team.name == MANAGEMENT
                and request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
