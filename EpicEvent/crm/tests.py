import pytest
from rest_framework.test import APIClient
from .models import Client, Contract, Event
# from users.models import User, Team
from users.models import Team, User


# ############################################################# #
# ########################  -FIXTURES-   ###################### #

@pytest.fixture
def client(db):
    return APIClient()


@pytest.fixture
def management_team(db):
    management_team = Team(name='MANAGEMENT')
    management_team.save()
    return Team.objects.get(name='MANAGEMENT')


@pytest.fixture
def sale_team(db):
    sale_team = Team(name='SALES')
    sale_team.save()
    return Team.objects.get(name='SALES')


@pytest.fixture
def support_team(db):
    support_team = Team(name='SUPPORT')
    support_team.save()
    return Team.objects.get(name='SUPPORT')


@pytest.fixture
def seller1(db, sale_team):
    User.objects.create_user(username="seller1",
                             password="pwd12345",
                             email="seller1@email.com",
                             team=sale_team)
    return User.objects.get(username="seller1")


@pytest.fixture
def seller1_login(client: APIClient, seller1):
    response = client.post('/login/',
                           {'username': 'seller1',
                            'password': 'pwd12345'})
    return response.data['access']


@pytest.fixture
def seller2(db, sale_team):
    User.objects.create_user(username="seller2",
                             password="pwd12345",
                             email="seller2@email.com",
                             team=sale_team)

    return User.objects.get(username="seller2")


@pytest.fixture
def seller2_login(client: APIClient, seller2):
    response = client.post('/login/',
                           {'username': 'seller2',
                            'password': 'pwd12345'})
    return response.data['access']


@pytest.fixture
def supporter1(db, support_team):
    User.objects.create_user(username="supporter1",
                             password="pwd12345",
                             email="supporter@email.com",
                             team=support_team)

    return User.objects.get(username="supporter1")


@pytest.fixture
def supporter1_login(client: APIClient, supporter1):
    response = client.post('/login/',
                           {'username': 'supporter1',
                            'password': 'pwd12345'})
    return response.data['access']


@pytest.fixture
def manager1(db, management_team):
    User.objects.create_user(username="manager1",
                             password="pwd12345",
                             email="supporter@email.com",
                             team=management_team)

    return User.objects.get(username="manager1")


@pytest.fixture
def manager1_login(client: APIClient, manager1):
    response = client.post('/login/',
                           {'username': 'manager1',
                            'password': 'pwd12345'})
    return response.data['access']


@pytest.fixture
def client1(db, seller1):
    return Client.objects.create(first_name="Jean",
                                 last_name="Martin",
                                 email="jmartin@email.com",
                                 mobile="06 06 06 06 06",
                                 sales_contact=seller1)


@pytest.fixture
def client2(db, seller1):
    return Client.objects.create(first_name="Fabienne",
                                 last_name="Marchand",
                                 email="fmarchand@email.com",
                                 mobile="06 07 07 07 07",
                                 sales_contact=None)


@pytest.fixture
def client3(db, seller2):
    return Client.objects.create(first_name="Vincent",
                                 last_name="Duval",
                                 email="vduval@email.com",
                                 mobile="06 07 07 07 07",
                                 sales_contact=seller2)


@pytest.fixture
def contract1(db, seller1, client1):
    return Contract.objects.create(status_sign=False,
                                   amount='10250.50',
                                   payment_due="2023-01-20",
                                   client=client1,
                                   sales_contact=seller1)


@pytest.fixture
def contract2(db, seller1, client1):
    return Contract.objects.create(status_sign=True,
                                   amount='999.50',
                                   payment_due="2023-02-20",
                                   client=client1,
                                   sales_contact=seller1)


@pytest.fixture
def event1(db, supporter1, contract1, seller1):
    return Event.objects.create(contract=contract1,
                                name='Feu d\'articices',
                                attendees="1200",
                                support_contact=supporter1)


@pytest.fixture
def event2(db, supporter1, contract2, seller1):
    return Event.objects.create(contract=contract2,
                                name='Repas annuel des retraités',
                                attendees="200",
                                support_contact=supporter1)

# ############################################################# #
# #############  TEST STR and @property models   ############## #


def test_full_name(client1: Client):
    assert client1.full_name == "Jean Martin - suivi par seller1 (SALES)"


def test_str_contract(contract1: Contract):
    assert str(contract1) == "N° 1  Jean Martin - Non signé "


def test_description_contract(contract1: Contract):
    assert contract1.description in "N° 2  Jean Martin - suivi par seller1 (SALES)"


def test_event(event1: Event):
    assert str(event1) in "Evènement N° 3  Jean Martin - Non signé  - suivi par supporter1 (SUPPORT)"


def test_description_event(event1: Event):
    assert event1.description in "Evènement N° 4  Jean Martin - Non signé  - Non terminé "


def test_event_has_support(event1: Event):
    assert event1.has_support is True


# ############################################################################
# ###########################  -Tests CLIENTS-  ##############################
# ############################################################################

def test_get_client_list_seller1(client, seller1_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Jean' in response.content
    assert b'Fabienne' in response.content
    assert b'Vincent' not in response.content


def test_not_get_client_list_seller1_for_seller2(client, seller2_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller2_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Vincent' in response.content
    assert b'Fabienne' in response.content
    assert b'Jean' not in response.content


def test_get_client_list_seller1_with_contract_for_supporter1(client, supporter1_login, client1, contract1,
                                                              client2, client3, event1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Fabienne' not in response.content
    assert b'Jean' in response.content


def test_get_client_list_sale_team_for_manager1(client, manager1_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + manager1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Vincent' in response.content
    assert b'Fabienne' in response.content
    assert b'Jean' in response.content


def test_view_client_detail_for_seller1(client, seller1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)

    response = client.get('/crm/clients/' + str(client1.id) + '/')
    assert response.status_code == 200


def test_seller1_can_post_new_client(client, seller1_login):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.post('/crm/clients/',
                           {'first_name': "Caroline",
                            'last_name': "Bouquet",
                            'email': "cbouquet@eamil.com",
                            'mobile': "06-88-77-66-55"}, format='json')
    assert response.status_code == 201


def test_supporter1_can_not_post_new_client(client, supporter1_login):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.post('/crm/clients/',
                           {'first_name': "Michel",
                            'last_name': "Plantu",
                            'email': "mplantu@amail.fr",
                            'mobile': "O655443322"}, format='json')
    assert response.status_code == 403


def test_update_client_detail_for_seller1(client, seller1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.put('/crm/clients/' + str(client1.id) + '/',
                          {'first_name': "Jean",
                           'last_name': "Martin",
                           'email': "jmartinchange@email.fr",
                           'phone': '0101010101',
                           'mobile': "123456789",
                           'company_name': 'EDF'}, format='json')
    assert response.status_code == 202


def test_delete_client_for_seller1(client, seller1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.delete('/crm/clients/' + str(client1.id) + '/')
    assert response.status_code == 204


# ############################################################################
# ###########################  -Tests CONTRACTS-  ############################
# ############################################################################


def test_get_contracts_list_for_seller1(client, seller1_login, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/contracts/')
    assert response.status_code == 200


def test_get_contracts_list_for_supporter1(client, supporter1_login, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.get('/crm/contracts/')
    assert response.status_code == 200


def test_seller1_can_post_new_contract(client, seller1_login, client2):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.post('/crm/contracts/',
                           {'amount': '999.99',
                            'payment_due': "2023-06-15",
                            'client': client2.id}, format='json')

    assert response.status_code == 201


def test_supporter1_not_authorized_to_post_new_contract(client, supporter1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.post('/crm/contracts/',
                           {'amount': "100",
                            'payment_due': "2023-07-20",
                            'client': client1.id}, format='json')

    assert response.status_code == 403


def test_view_contract_detail_for_seller1(client, seller1_login, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/contracts/' + str(contract1.id) + '/')
    assert response.status_code == 200


def test_update_contract_not_sign_detail_for_seller1(client, seller1_login, contract1, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.put('/crm/contracts/' + str(contract1.id) + '/',
                          {'status_sign': True,
                           'amount': '10250.50',
                           'payment_due': "2023-08-20",
                           'client': client1.id}, format='json')
    assert response.status_code == 202


def test_cant_delete_contract_signed(client, seller1_login, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.delete('/crm/contracts/' + str(contract1.id) + '/')
    assert response.status_code == 405

# ############################################################################
# #############################  -Tests EVENTS-  #############################
# ############################################################################


def update_event1(supporter1):
    Event.objects.filter(pk=event1.pk).update(support_contact=supporter1)


def test_get_events_list_for_seller1(client, seller1_login, event1, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/events/')
    assert response.status_code == 200


def test_get_events_list_for_supporter1(client, supporter1_login, event1, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.get('/crm/events/')
    assert response.status_code == 200


def test_seller1_can_post_new_event(client, seller1_login, client1, contract2):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.post('/crm/events/',
                           {'contract': contract2.id,
                            'attendees': '160',
                            'event_date': "2022-02-12",
                            'notes': "Mon événement"}, format='json')
    assert response.status_code == 201


def test_supporter1_not_authorized_to_post_new_event(client, supporter1_login, contract2, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.post('/crm/events/',
                           {'contract': contract2.id,
                            'attendees': '160',
                            'event_date': "2022-02-12",
                            'notes': 'Mon événement'}, format='json')
    assert response.status_code == 403


def test_seller1_can_view_event_detail(client, seller1_login, event1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/events/' + str(event1.id) + '/')
    assert response.status_code == 200


def test_supporter1_can_view_event_detail(client, supporter1_login, event1, contract1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.get('/crm/events/' + str(event1.id) + '/')
    assert response.status_code == 200


def test_supporter1_can_update_event_detail(client, supporter1_login, event2, client1, contract2):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.put('/crm/events/' + str(event2.id) + '/',
                          {'contract': contract2.id,
                           'attendees': 2200,
                           'name': "Feu d'\artifices modifié",
                           'client': client1.id}, format='json')
    assert response.status_code == 202


def test_supporter1_cant_delete_event(client, supporter1_login, event1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.delete('/crm/events/' + str(event1.id) + '/')
    assert response.status_code == 403


def test_get_events_list_with_filtering(client, seller1_login, event1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/events/?event_date__gte=2022-12-31')
    assert response.status_code == 200
