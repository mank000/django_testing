import pytest

from django.conf import settings

from news.forms import CommentForm


def test_count_of_news_and_right_order(client, many_news,
                                       many_comments, home_url):
    """Проверяет количество, сортировку новостей и комментариев"""
    response = client.get(home_url)
    news_objects = response.context['object_list']
    all_date_news = [news.date for news in news_objects]
    sorted_dates_news = sorted(all_date_news, reverse=True)
    assert (response.context[
        'object_list'].count() <= settings.NEWS_COUNT_ON_HOME_PAGE)
    assert all_date_news == sorted_dates_news


@pytest.mark.django_db
def test_right_order_comments(client, many_comments):
    """Проверяет сортировку комментариев"""
    comments_objects = many_comments.comment_set.all()
    all_date_comments = [comment.created for comment in comments_objects]
    sorted_dates_comments = sorted(all_date_comments)
    assert all_date_comments == sorted_dates_comments


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, watch',
    ((pytest.lazy_fixture('not_author_client'), True),
        (pytest.lazy_fixture('client'), False))
)
def test_anonymous_user_cant_get_form(user, news, watch, detail_url):
    """
    Анонимному пользователю недоступна
    форма для отправки комментария на
    странице отдельной новости, а авторизованному доступна.
    """
    url = detail_url(news.id)
    response = user.get(url)
    if watch:
        assert "form" in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert "form" not in response.context
