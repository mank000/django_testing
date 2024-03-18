from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


OK_STATUS = HTTPStatus.OK
NOT_FOUND_STATUS = HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, user, status',
    (
        (lf('home_url'),
         lf('client'),
         OK_STATUS),
        (lf('detail_url'),
         lf('client'),
         OK_STATUS),
        (lf('edit_url'),
         lf('not_author_client'),
         NOT_FOUND_STATUS),
        (lf('delete_url'),
         lf('not_author_client'),
         NOT_FOUND_STATUS),
        (lf('logout_url'),
         lf('client'),
         OK_STATUS),
        (lf('login_url'),
         lf('client'),
         OK_STATUS),
        (lf('signup_url'),
         lf('client'),
         OK_STATUS)
    )
)
def test_home_page_avaiblity_for_user(user, name, status):
    """Главная и отдельная страница от лица анонимного пользователя."""
    response = user.get(name)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    (lf('edit_url'), lf('delete_url'))
)
def test_not_avaible_edit_delete_for_anonymous(client, name, login_url):
    """Редиректы для анонимных пользователей."""
    response = client.get(name)
    expected_url = f'{login_url}?next={name}'
    assertRedirects(response, expected_url)
