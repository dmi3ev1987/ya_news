from datetime import datetime, timedelta
import pytest

from django.urls import reverse
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


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
        title='Тестовая новость.',
        text='Просто текст.',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=timezone.now(),
    )
    return comment


@pytest.fixture
def all_comments_for_news(author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def detail_url_news(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def detail_url_for_comments(all_comments_for_news):
    return reverse('news:detail', args=(all_comments_for_news.id,))


@pytest.fixture
def delete_url(comment_id_for_args):
    return reverse('news:delete', args=(comment_id_for_args))


@pytest.fixture
def edit_url(comment_id_for_args):
    return reverse('news:edit', args=(comment_id_for_args))


@pytest.fixture
def url_to_comments(news_id_for_args):
    news_url = reverse('news:detail', args=(news_id_for_args))
    return news_url + '#comments'


@pytest.fixture
def form_data():
    return {
        'text': COMMENT_TEXT,
    }


@pytest.fixture
def new_form_data():
    return {
        'text': NEW_COMMENT_TEXT,
    }
