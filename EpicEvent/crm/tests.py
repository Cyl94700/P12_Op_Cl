import pytest
from rest_framework.test import APIClient
from .models import Client
# from users.models import User, Team
from users.models import Team, User


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

# ############################################################################
# ###########################  Tests CLIENTS  ##############################
# ############################################################################


def test_get_client_list_for_sale_team_seller1(client, seller1_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Jean' in response.content
    assert b'Fabienne' in response.content
    assert b'Vincent' not in response.content


def test_not_get_client_list_for_sale_team_seller2(client, seller2_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller2_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Vincent' in response.content
    assert b'Fabienne' in response.content
    assert b'Jean' not in response.content


def test_not_get_client_list_for_sale_team_supporter1(client, supporter1_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + supporter1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 403
    assert b'Vincent' not in response.content
    assert b'Fabienne' not in response.content
    assert b'Jean' not in response.content


def test_not_get_client_list_for_sale_team_manager1(client, manager1_login, client1, client2, client3):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + manager1_login)
    response = client.get('/crm/clients/')
    assert response.status_code == 200
    assert b'Vincent' in response.content
    assert b'Fabienne' in response.content
    assert b'Jean' in response.content


def test_view_client_detail(client, seller1_login, client1):
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


def test_update_client_detail(client, seller1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.put('/crm/clients/' + str(client1.id) + '/',
                          {'first_name': "Jean",
                           'last_name': "Martin",
                           'email': "jmartinchange@email.fr",
                           'phone': '0101010101',
                           'mobile': "123456789",
                           'company_name': 'EDF'}, format='json')
    assert response.status_code == 202


def test_delete_client(client, seller1_login, client1):
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + seller1_login)
    response = client.delete('/crm/clients/' + str(client1.id) + '/')
    assert response.status_code == 204
