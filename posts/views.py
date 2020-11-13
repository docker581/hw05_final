from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import User, Post, Group, Follow
from .forms import PostForm, CommentForm


def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404,
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 
        'index.html', 
        {
            'page': page, 
            'paginator': paginator,
        }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number) 
    return render(
        request, 
        'group.html', 
        {
            'group':group, 
            'page': page, 
            'paginator': paginator,
        }
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author=request.user
            instance.save()
            return redirect('index')
    return render(
        request, 
        'new.html', 
        {
            'form': form, 
            'tab_title': 'Новая запись',
            'form_title': 'Добавить запись',
            'form_button_name': 'Добавить',
        }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)  
    posts = Post.objects.filter(author=author)
    posts_count = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author.following.filter(user=request.user.id).exists()
    author_followers = author.following.count()
    author_followings = author.follower.count()      
    return render(
        request, 
        'profile.html', 
        {
            'author': author,
            'page': page,
            'posts_count': posts_count,
            'paginator': paginator,
            'following': following,
            'author_followers': author_followers,
            'author_followings': author_followings,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    posts_count = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.all()
    author = User.objects.get(username=username)
    following = author.following.filter(user=request.user.id).exists()
    author_followers = author.following.count()
    author_followings = author.follower.count()      
    return render(
        request, 
        'post.html',
        {
            'form': form,
            'author': post.author,
            'post': post,
            'posts_count': posts_count,
            'comments': comments,
            'following': following,
            'author_followers': author_followers,
            'author_followings': author_followings,
        }
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author=request.user
            instance.post = post
            instance.save()
            return redirect('post', username, post_id)
    return redirect('post', username, post_id)  


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None, 
        files=request.FILES or None, 
        instance=post
    )
    if request.method == 'POST':
        if form.is_valid():
            post = Post.objects.get(id=post_id)
            post.text = form.cleaned_data['text'] 
            post.group = form.cleaned_data['group']
            post.image = form.cleaned_data['image']
            post.save()
            return redirect('post', username, post_id)        
    return render(
        request, 
        'new.html', 
        {
            'form': form, 
            'post': post,
            'tab_title': 'Изменение записи',
            'form_title': 'Редактировать запись',
            'form_button_name': 'Сохранить',
        }
    )


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'page': page,
            'paginator': paginator,
        }
    )


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.get(author=author, user=request.user).delete()
    return redirect('profile', username)
