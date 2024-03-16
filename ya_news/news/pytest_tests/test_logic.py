from http import HTTPStatus

from django.urls import reverse
import pytest


@pytest.mark.parametrize(
    'user, answer', (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('not_author_client'), 1)
    )
)
def test_anonymous_cant_send_comment(user,
                                     answer,
                                     news,
                                     form_data_for_comment):
    """
    Анонимный пользователь не может отправить комментарий.
    Авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.id, ))
    user.post(url, data=form_data_for_comment)
    assert news.comment_set.all().count() == answer


def test_ban_words(not_author_client,
                   news,
                   form_data_for_comment_with_badwords):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id, ))
    response = not_author_client.post(url,
                                      data=form_data_for_comment_with_badwords)
    assert 'block' in response.context
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
    response = user.post(url)
    print(response)
    assert response.status_code != answer
