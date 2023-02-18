from django.contrib import admin

from .models import Client, Contract, Event


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Client/Prospect Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "mobile",
                    "company_name",
                )
            },
        ),
        ("Sales", {"fields": ("sales_contact",)}),

        ("Info", {"fields": ("datetime_created", "datetime_updated")}),
    )
    readonly_fields = ("datetime_created", "datetime_updated")
    list_display = (
        "full_name",
        "company_name",
        "email",
        "phone",
        "mobile",
        "sales_contact",
    )
    # list_filter = ("sales_contact", admin.RelatedOnlyFieldListFilter),
    list_filter = ("sales_contact",)
    search_fields = ("first_name", "last_name", "company_name", "sales_contact")

    @staticmethod
    def full_name(obj):
        return f"{obj.last_name}, {obj.first_name}"


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contract Info", {"fields": ("client", "amount", "payment_due")}),
        ("Sales", {"fields": ("status_sign", "sales_contact")}),
        ("Info", {"fields": ("datetime_created", "datetime_updated")}),
    )
    readonly_fields = ("datetime_created", "datetime_updated")
    list_display = (
        "contract_number",
        "sales_contact",
        "client",
        "amount",
        "payment_due",
        "status_sign",
    )
    list_filter = ("status_sign", "sales_contact")
    search_fields = ("contract_number", "client__last_name")

    @staticmethod
    def contract_number(obj):
        return f"Contract #{obj.id}"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Event Info",
            {
                "fields": (
                    "attendees",
                    "event_date",
                    "status",
                )
            },
        ),
        ("Support", {"fields": ("support_contact", "notes")}),
        ("Info", {"fields": ("datetime_created", "datetime_updated")}),
    )
    readonly_fields = ("datetime_created", "datetime_updated")
    list_display = (
        "support_contact",
        "attendees",
        "event_date",
        "status",
    )
    list_filter = ("status", "support_contact")
    search_fields = ("name", "location", "client__last_name")


"""from django.contrib import admin

from .models import Client, Contract, Event

admin.site.register(Client)
admin.site.register(Contract)
admin.site.register(Event)
"""