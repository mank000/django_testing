from random import choice

from pytest_django.asserts import assertFormError
import pytest

from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, increase', (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('not_author_client'), 1),
    )
)
def test_anonymous_cant_send_comment(user, news, detail_url, increase):
    """Отправка комментария пользователем."""
    url = detail_url
    before_user_post = news.comment_set.all().count()
    user.post(url, data={'text': 'text1'})
    after_user_post = news.comment_set.all().count()
    assert before_user_post + increase <= after_user_post
    if increase == 1:
        assert news.comment_set.last().text == 'text1'


def test_ban_words(not_author_client, news, detail_url):
    """Запрещенные слова в комментарии."""
    url = detail_url
    before_comments = news.comment_set.all().count()
    response = not_author_client.post(url,
                                      data={'text': choice(BAD_WORDS)})
    assertFormError(response, 'form', 'text', WARNING)
    after_comments = news.comment_set.all().count()
    assert before_comments == after_comments


@pytest.mark.parametrize(
    'user, answer', (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('not_author_client'), 0)
    )
)
def test_author_edit_comment(user, answer, comments, edit_url):
    before_text = comments.text
    user.post(edit_url, data={'text': 'not'})
    comments.refresh_from_db()
    after_text = comments.text
    if answer:
        assert before_text != after_text
    else:
        assert before_text == after_text


@pytest.mark.parametrize(
    'user, increase', (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('not_author_client'), 0)
    )
)
def test_delete_comment(user, increase, comments, delete_url):
    """Удаление комментария пользователями."""
    before = comments.news.comment_set.all().count()
    user.post(delete_url)
    after = comments.news.comment_set.all().count()
    assert before - increase == after
