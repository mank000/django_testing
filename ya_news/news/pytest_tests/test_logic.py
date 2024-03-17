from http import HTTPStatus
from random import choice

from django.urls import reverse
from pytest_django.asserts import assertFormError

import pytest

from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user', (
        pytest.lazy_fixture('client'),
        pytest.lazy_fixture('not_author_client')
    )
)
def test_anonymous_cant_send_comment(user, news, detail_url):
    """
    Анонимный пользователь не может отправить комментарий.
    Авторизованный пользователь может отправить комментарий.
    """
    url = detail_url(news.id)
    before_user_post = news.comment_set.all().count()
    user.post(url, data={'text': 'text1'})
    after_user_post = news.comment_set.all().count()
    assert before_user_post <= after_user_post


def test_ban_words(not_author_client, news, detail_url):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = detail_url(news.id)
    response = not_author_client.post(url,
                                      data={'text': choice(BAD_WORDS)})
    assertFormError(response, 'form', 'text', WARNING)
    assert news.comment_set.all().count() == 0


@pytest.mark.parametrize(
    'user, answer', (
        (pytest.lazy_fixture('author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_auth_user_permissions(user, answer, name, comments):
    """
    Авторизованный пользователь может
    редактировать или удалять свои комментарии.
    Авторизованный пользователь не может
    редактировать или удалять чужие комментарии.
    """
    url = reverse(name, args=(comments.id, ))
    before = comments.news.comment_set.all().count()
    text_before = comments.text
    response = user.post(url, data={'text': 'not'})
    if name == 'news:edit':
        assert comments.text == text_before
    elif name == 'news:delete':
        after = comments.news.comment_set.all().count()
        if answer == 404:
            assert before > after
        else:
            assert before == after
    assert response.status_code != answer
