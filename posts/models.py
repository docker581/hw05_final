from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальное имя',
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name_plural='Группы'
    
    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        'Дата',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
    )
    image = models.ImageField(
        upload_to='posts/', 
        blank=True, 
        null=True,
        verbose_name='Изображение',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Список постов'

    def __str__(self):
        return self.text[:10]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(
        'Дата',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:10]   


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    class Meta:
        models.UniqueConstraint(
            fields=['author', 'user'],
            name='author_user',
        )
        verbose_name_plural='Подписки'
    
    def __str__(self):
        return self.author.username
