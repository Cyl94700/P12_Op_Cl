from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class Client(models.Model):
    """
    Client avec ou sans contrat(s)
    Chaque client est relié à une équipe du groupe de vente.
    Un utilisateur de l'équipe de vente peut créer des clients potentiels sans contact client.
    L'utilisateur de l'équipe de management attribue le contact client, ce qui convertit le client potentiel
    en client actif.
    """

    first_name = models.CharField(max_length=25, help_text=_("Prénom"))
    last_name = models.CharField(max_length=25, help_text=_("Nom"))
    email = models.EmailField(max_length=100, help_text=_("Email client"))
    phone = models.CharField(max_length=20, help_text=_("Télephone client fixe"), blank=True)
    mobile = models.CharField(max_length=20, help_text=_("Téléphone client mobile"))
    company_name = models.CharField(max_length=250, help_text=_("Société client si professionnel"), blank=True)
    sales_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                      limit_choices_to={"team_id": 2},
                                      help_text=_("Contact vendeur assigné par l'équipe management"))
    datetime_created = models.DateTimeField(auto_now_add=True, help_text=_("Date de création client"))
    datetime_updated = models.DateTimeField(auto_now=True, help_text=_("Date de modification client"))

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name_plural = _("Clients")

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def full_name(self):
        return "{} {} - suivi par {}".format(self.first_name, self.last_name, self.sales_contact)

    @property
    def has_sales(self):
        """
        True renvoué si le client a un sales_contact
        """
        if self.sales_contact is None:
            return False
        else:
            return True


class Contract(models.Model):
    """
    Contrats
    Chaque contrat est lié à un client et un membre de l'équipe de vente.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, help_text=_("Client signataire"),
                               related_name="contract", )
    sales_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                      limit_choices_to={"team_id": 2},
                                      help_text=_("Contact vendeur attribué par l'équipe management"))
    status_sign = models.BooleanField(default=False, help_text=_("contrat signé O/N"))
    amount = models.DecimalField(max_digits=9, decimal_places=2, help_text=_("Montant du contrat"))
    payment_due = models.DateField(help_text=_("Date de paiement Format: AAAA-MM-JJ"))

    datetime_created = models.DateTimeField(auto_now_add=True,
                                            help_text=_("Date de création du contrat"))
    datetime_updated = models.DateTimeField(auto_now=True,
                                            help_text=_("Date de modification du contrat"))

    class Meta:
        ordering = ['client', '-datetime_created']
        verbose_name_plural = _("Contrats")

    def __str__(self):
        if self.status_sign is False:
            sign = "Non signé"
        else:
            sign = "Signé"
        return "N° {}  {} - {} ".format(self.id, self.client, sign)

    @property
    def description(self):
        return "N° {}  {} - suivi par {}".format(self.id, self.client, self.sales_contact)


class Event(models.Model):
    """
    Evénement client
    Chaque événement est lié à un client et un membre de l'équipe support attribué par l'équipe de management
    """
    contract = models.OneToOneField(to=Contract, on_delete=models.CASCADE, limit_choices_to={"status_sign": True},
                                    related_name="event")
    name = models.CharField(max_length=100, help_text=_("Nom"), null=True, blank=True,)

    attendees = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True,
                                    help_text=_("Nombre d'invités"))
    event_date = models.DateField(null=True, blank=True, help_text=_("Date de l'évènement Format: AAAA-MM-JJ"))
    notes = models.TextField(help_text=_("Notes"), blank=True)

    support_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                        limit_choices_to={"team_id": 3},
                                        blank=True, help_text=_("Contact support"), related_name="events")

    status = models.BooleanField(default=False, help_text=_("Terminé O/N"))
    datetime_created = models.DateTimeField(auto_now_add=True, help_text=_("Date création évènement"))
    datetime_updated = models.DateTimeField(auto_now=True, help_text=_("Date de modification événement"))

    class Meta:
        ordering = ['status', 'event_date']
        verbose_name_plural = _("Evènements")

    def __str__(self):
        return "Evènement {} - suivi par {}".format(
            self.contract, self.support_contact)

    @property
    def description(self):
        return "Evènement {} - {} ".format(
            self.contract, self.status)

    @property
    def has_support(self):
        """
        True renvoyé si l'événement a un support_contact
        """
        if self.support_contact is None:
            return False
        else:
            return True
