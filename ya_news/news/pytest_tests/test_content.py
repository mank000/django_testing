from django.conf import settings
from django.urls import reverse


def test_count_of_news_and_right_order(client, many_news_and_comments):
    """
    1)Количество новостей на главной странице — не более 10.
    2)Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    3)Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_date_news = [news.date for news in object_list]
    sorted_dates_news = sorted(all_date_news, reverse=True)
    object_list_comments = many_news_and_comments.comment_set.all()
    all_date_comments = [comment.created for comment in object_list_comments]
    sorted_dates_comments = sorted(all_date_comments, reverse=True)
    assert (response.context[
        'object_list'].count() <= settings.NEWS_COUNT_ON_HOME_PAGE)
    assert all_date_news == sorted_dates_news
    assert all_date_comments == sorted_dates_comments


def test_anonymous_user_cant_get_form(not_author_client, client, news):
    """
    Анонимному пользователю недоступна
    форма для отправки комментария на
    странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=(news.id, ))
    response = client.get(url)
    assert "form" not in response.context
    response = not_author_client.get(url)
    assert "form" in response.context
