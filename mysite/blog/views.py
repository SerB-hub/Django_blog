from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from . forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

# Create your views here.

'''
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

'''


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 поста на каждой странице
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, поставим первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, доставить последнюю страницу результатов
        posts = paginator.page(paginator.num_pages)

    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', 'body')
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')

    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag,
                   'request': request.user.is_authenticated,
                   'form': form,
                   'query': query,
                   'results': results})


'''
def post_list(request):
    posts = Post.published.all()
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})
'''


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # Список активных комментариев к этой записи
    comments = post.comments.filter(active=True)
    new_comment = None
    auth_user = False
    if request.method == 'POST':
        # Комментарий был опубликован
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создайте объект Comment, но пока не сохраняйте в базу данных
            new_comment = comment_form.save(commit=False)
            if request.user.is_authenticated and \
                    (request.user.username == new_comment.name):
                # Назначить текущий пост комментарию
                new_comment.post = post
                # Назначить пользователя комментарию
                new_comment.author = request.user
                # Сохранить комментарий в базе данных
                new_comment.save()
            else:
                new_comment.name = 'Anonymous - {}'.format(new_comment.name)
                # Назначить текущий пост комментарию
                new_comment.post = post
                # Назначить пользователя комментарию
                new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
        .order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts,
                                                     'auth_user': auth_user})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', 'body')
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
            # Поиск по схожести триграмм
            # results = Post.objects.annotate(
            #     similarity=TrigramSimilarity('title', query),
            # ).filter(similarity__gt=0.3).order_by('-similarity')
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})


def post_share(request, post_id):
    # Получить пост по id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма была отправлена
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы прошли проверку
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading " {}"'.format(cd['name'], cd['email'],
                                                                    post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url,
                                                                     cd['name'], cd['comments'])
            send_mail(subject, message, 'leisuretimeflash@gmail.com', [cd['to']])
            sent = True
    else:
            form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})
