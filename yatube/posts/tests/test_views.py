import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms


from ..models import Follow, Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Katya',)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        cache.clear()

    def test_views_cor_templates(self):
        """Проверка использования правильных html-шаблонов во view-функциях."""
        templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Katya'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for key, value in templates_names.items():
            with self.subTest(key=key):
                response = self.auth_client.get(key)
                self.assertTemplateUsed(response, value)

    def test_views_cor_context_index(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image.name
        self.assertEqual(post_author_0, 'Katya')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_views_cor_context_group_list(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.auth_client.
                    get(reverse('posts:group_list', kwargs={'slug':
                                'test-slug'})))
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_views_cor_context_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.auth_client.get(reverse('posts:profile',
                    args={'Katya'})))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image.name
        self.assertEqual(post_author_0, 'Katya')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_views_cor_context_post_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.auth_client.get(reverse('posts:post_detail',
                    args={'1'})))
        self.assertEqual(response.context.get('post').author.username, 'Katya')
        self.assertEqual(response.context.get('post').text, 'Тестовый пост')
        self.assertEqual(response.context.get('post').group.title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('post').image.name,
                         'posts/small.gif')

    def test_views_cor_context_post_create(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for key, value in form_fields.items():
            with self.subTest(key=key):
                form_field = response.context.get('form').fields.get(key)
                return self.assertIsInstance(form_field, value)

    def test_views_cor_context_post_edit(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:post_edit',
                                        args={'1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for key, value in form_fields.items():
            with self.subTest(key=key):
                form_field = response.context.get('form').fields.get(key)
                self.assertIsInstance(form_field, value)

    def test_cache(self):
        """Проверка работы кэша на главной странице."""
        response = self.auth_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response_before_cache_cleaning = (self.auth_client.get(reverse
                                          ('posts:index')))
        posts_before_cache_cleaning = response_before_cache_cleaning.content
        self.assertEqual(posts_before_cache_cleaning, posts)
        cache.clear()
        response_after_cache_cleaning = (self.auth_client.get(reverse
                                         ('posts:index')))
        posts_after_cache_cleaning = response_after_cache_cleaning.content
        self.assertNotEqual(posts_before_cache_cleaning,
                            posts_after_cache_cleaning)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Katya',)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post_list = []
        for i in range(0, 14):
            post_list.append(
                Post(
                    text=f'Тестовый пост {i}',
                    author=cls.user,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(post_list)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_paginator(self):
        """Paginator работает корректно."""
        reverse_posts = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 4,
            reverse('posts:group_list', args={'test-slug'}): 10,
            reverse('posts:group_list', args={'test-slug'}) + '?page=2': 4,
            reverse('posts:profile', kwargs={'username': 'Katya'}): 10,
            reverse('posts:profile',
                    kwargs={'username': 'Katya'}) + '?page=2': 4,
        }
        for key, value in reverse_posts.items():
            with self.subTest(key=key):
                cache.clear()
                response = self.auth_client.get(key)
                self.assertEqual(len(response.context['page_obj']), value)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='Author')
        cls.user2 = User.objects.create_user(username='Follower')

    def setUp(self):
        self.author = Client()
        self.author.force_login(self.user1)
        self.follower = Client()
        self.follower.force_login(self.user2)

    def test_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей."""
        followers = Follow.objects.count()
        self.follower.get(reverse('posts:profile_follow', args={'Author'}))
        self.assertEqual(Follow.objects.count(), followers + 1)

    def test_unfollow(self):
        """Авторизованный пользователь может
        удалять других пользователей из своих подписок."""
        followers = Follow.objects.count()
        self.follower.get(reverse('posts:profile_follow', args={'Author'}))
        self.follower.get(reverse('posts:profile_unfollow', args={'Author'}))
        self.assertEqual(Follow.objects.count(), followers)

    def test_new_post_appear_for_subscribers(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан."""
        self.follower.get(reverse('posts:profile_follow', args={'Author'}))
        Post.objects.create(
            author=self.user1,
            text='Тестовый пост'
        )
        response = self.follower.get(reverse('posts:follow_index'))
        objects = len(response.context['page_obj'])
        self.assertEqual(objects, 1)

    def test_new_post_not_appear_for_non_subscribers(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто на него  не подписан."""
        Post.objects.create(
            author=self.user1,
            text='Тестовый пост'
        )
        response = self.follower.get(reverse('posts:follow_index'))
        objects = len(response.context['page_obj'])
        self.assertEqual(objects, 0)
