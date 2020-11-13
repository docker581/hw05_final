from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files import File

from posts.models import User, Post, Group, Follow, Comment

import mock


class ProjectTests2(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='johnny')
        self.authorized_client = Client()        
        self.authorized_client.force_login(self.user)
        self.unauthorized_client = Client()
        self.group = Group.objects.create(
            title='first group', 
            slug='first', 
            description='description',
        )

        self.new_user = User.objects.create_user(username='mike')
        self.new_post = Post.objects.create(
            author = self.new_user,
            text = 'post from new user',
            group = self.group,
        )       

    def test_404(self):
        response = self.unauthorized_client.get('some_page')
        self.assertEqual(response.status_code, 404)  

    def test_image_check(self): 
        image = mock.MagicMock(spec=File)
        image.name = 'test.jpg' 
        Post.objects.create(
            text='some text', 
            author=self.user, 
            group=self.group,
            image=image, 
        )
        new_post_id = Post.objects.count()    
        urls = [
            reverse('index'),
            reverse('profile', args=(self.user.username,)), 
            reverse('post', args=(self.user.username, new_post_id)),
            reverse('group_posts', args=(self.group.slug,)),
        ]
        for url in urls:
            with self.subTest():
                if url == reverse('index'):
                    cache.clear() 
                response = self.authorized_client.get(url)
                self.assertContains( 
                    response,  
                    '<img',  
                    status_code=200, 
                )

    def test_not_image_check(self):      
        with open('requirements.txt','rb') as img:
            response = self.authorized_client.post(
                reverse('new_post'), 
                {
                    'author': self.user, 
                    'text': 'text with image',
                    'group': self.group.id, 
                    'image': img,
                }
            )
        message = ('Загрузите правильное изображение. ' 
                  'Файл, который вы загрузили, ' 
                  'поврежден или не является изображением.')
        self.assertFormError(
            response, 
            'form', 
            'image', 
            message,
        )

    def test_cache_check(self):
        key = make_template_fragment_key('index_page')
        old_response = self.authorized_client.get(reverse('index'))
        self.authorized_client.post(
            reverse('new_post'), 
            {
                'author': self.user, 
                'text': 'text with image',
                'group': self.group.id, 
            }
        )
        new_response = self.authorized_client.get(reverse('index'))
        self.assertEqual(old_response.content, new_response.content)
        cache.touch(key, 0)
        newer_response = self.authorized_client.get(reverse('index'))
        self.assertNotEqual(old_response.content, newer_response.content)

    def test_followers_count(self):
        followers = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', args=(self.new_user.username,))
        )
        self.assertEqual(Follow.objects.count(), followers + 1)
        self.authorized_client.get(
            reverse('profile_unfollow', args=(self.new_user.username,))
        )
        self.assertEqual(Follow.objects.count(), followers)    

    def test_subscribe(self):
        old_response = self.authorized_client.get(reverse('follow_index'))
        self.authorized_client.get(
            reverse('profile_follow', args=(self.new_user.username,))
        )
        new_response = self.authorized_client.get(reverse('follow_index'))
        self.assertNotEqual(old_response.content, new_response.content)

    def test_unsubscribe(self):
        old_response = self.authorized_client.get(reverse('follow_index'))
        self.authorized_client.get(
            reverse('profile_follow', args=(self.new_user.username,))
        )    
        self.authorized_client.get(
            reverse('profile_unfollow', args=(self.new_user.username,))
        )
        new_response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(old_response.content, new_response.content)

    def test_authorized_client_comment(self):
        comments = Comment.objects.count()
        self.authorized_client.post(
            reverse(
                'add_comment', 
                args=(self.new_user.username, self.new_post.id),
            ),
            {
                'author': self.authorized_client,
                'post': self.new_post,
                'text': 'text from authorized client',
            }
        )
        self.assertEqual(Comment.objects.count(), comments + 1)

    def test_unauthorized_client_comment(self):
        comments = Comment.objects.count()    
        self.unauthorized_client.post(
            reverse(
                'add_comment', 
                args=(self.new_user.username, self.new_post.id),
            ),
            {
                'author': self.unauthorized_client,
                'post': self.new_post,
                'text': 'text from unauthorized client',
            }
        )
        self.assertNotEqual(Comment.objects.count(), comments + 1)
