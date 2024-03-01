from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            form_data,
                                            detail_url_news):
    client.post(detail_url_news, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


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
                                 form_data,
                                 news,
                                 detail_url_news):
    response = parametrized_client.post(detail_url_news, data=form_data)
    assertRedirects(response, f'{detail_url_news}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
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
def test_user_cant_use_bad_words(parametrized_client, detail_url_news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = parametrized_client.post(detail_url_news, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client,
                                   delete_url,
                                   url_to_comments,):
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url,):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client,
                                 edit_url,
                                 url_to_comments,
                                 new_form_data,
                                 comment):
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                edit_url,
                                                new_form_data,
                                                form_data,
                                                comment):
    response = not_author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
