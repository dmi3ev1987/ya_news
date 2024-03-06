from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            news):
    detail_url_news = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT, }
    comments_count_before = Comment.objects.count()
    client.post(detail_url_news, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.parametrize(
    'parametrized_client, comment_author',
    (
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('author')),
        (pytest.lazy_fixture('not_author_client'),
         pytest.lazy_fixture('not_author'))
    )
)
def test_user_can_create_comment(parametrized_client,
                                 comment_author,
                                 news,):
    detail_url_news = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT, }
    comments_count_before = Comment.objects.count()
    response = parametrized_client.post(detail_url_news, data=form_data)
    assertRedirects(response, f'{detail_url_news}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == comment_author


@pytest.mark.parametrize(
    'parametrized_client',
    (
        pytest.lazy_fixture('author_client'),
        pytest.lazy_fixture('not_author_client'),
    )
)
def test_user_cant_use_bad_words(parametrized_client, news):
    detail_url_news = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = parametrized_client.post(detail_url_news, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_author_can_delete_comment(author_client,
                                   comment,
                                   news,):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  comment,):
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_count_before = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


def test_author_can_edit_comment(author_client,
                                 news,
                                 comment):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    new_form_data = {'text': NEW_COMMENT_TEXT, }
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': COMMENT_TEXT, }
    new_form_data = {'text': NEW_COMMENT_TEXT, }
    response = not_author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
