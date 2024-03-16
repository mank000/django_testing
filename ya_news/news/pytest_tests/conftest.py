from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings

from news.forms import BAD_WORDS
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
def news(author_client):
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def get_news_id(author_client):
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return (news.id, )


@pytest.fixture
def comments(author_client, author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    comment = Comment.objects.create(
        news=news,
        text='lajsdk',
        author=author
    )
    return comment


@pytest.fixture
def many_news_and_comments(author_client, author):
    news = [
        News.objects.create(
            title=f'заголовок {i}',
            text=f'текст {i}',
            date=datetime.today() - timedelta(days=i)
        ) for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 2)]
    [Comment.objects.create(
        news=news[0],
        text=f'text{i}',
        author=author,
        created=datetime.now() + timedelta(days=i)
    ) for i in range(4)]
    return news[0]


@pytest.fixture
def form_data_for_comment(news, author):
    return {'news': news,
            'text': 'textdata',
            'author': author,
            }


@pytest.fixture
def form_data_for_comment_with_badwords(news, author):
    return {'news': news,
            'text': f'textdata {BAD_WORDS[1]}',
            'author': author,
            }
