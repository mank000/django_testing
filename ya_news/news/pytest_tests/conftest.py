from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comments(author, news):
    comment = Comment.objects.create(
        news=news,
        text='lajsdk',
        author=author
    )
    return comment


@pytest.fixture
def many_news(author):
    news = [
        News(
            title=f'заголовок {i}',
            text=f'текст {i}',
            date=datetime.today() - timedelta(days=i)
        ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 2)]
    News.objects.bulk_create(news)
    for n in news:
        n.save()
    return news[0]


@pytest.fixture
def many_comments(news, author):
    now = timezone.now()
    for i in range(11):
        comment = Comment.objects.create(
            news=news, author=author, text=f'text {i}',
        )
        comment.created = now + timedelta(days=i)
        comment.save()
    return news


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url():
    def _get_news_detail_url(num):
        return reverse('news:detail', args=(num, ))
    return _get_news_detail_url
