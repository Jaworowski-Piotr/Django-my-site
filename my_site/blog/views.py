from django.shortcuts import render, Http404
from .models import Post
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views.generic import ListView, DetailView
from django.views import View

from .forms import CommentForm


def get_date(post):
    return post['date']


# def starting_page(request):
#     latest_posts = Post.objects.all().order_by("-date")[:3]  ###django sam przekształci aby samemu zabrać 3 ostatnie posty
#     return render(request, "blog/index.html", {
#         "posts": latest_posts
#     })

class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super(StartingPageView, self).get_queryset()
        date = queryset[:3]
        return date


# def posts(request):
#     all_posts = Post.objects.all().order_by("-date")
#     return render(request, "blog/all-posts.html", {
#         "all_posts": all_posts
#     })

class AllPostView(ListView):
    template_name = 'blog/all-posts.html'
    model = Post
    ordering = ["-date"]
    context_object_name = 'all_posts'


# def post_detail(request, slug):
#     try:
#         identified_post = Post.objects.get(slug=slug)
#     except:
#         return Http404
#     return render(request, "blog/post-detail.html", {
#         "post": identified_post,
#         "tags": identified_post.tags.all()
#     })

# class SinglePostView(DetailView):
#     template_name = 'blog/post-detail.html'
#     model = Post
#     # Django sam będzie szulał po dynamicznie przekazyanym parametrze
#     def get_context_data(self, **kwargs):
#         context = super(SinglePostView, self).get_context_data(**kwargs)
#         context['tags'] = self.object.tags.all() #sposób na odwołanie się do instancji obiektu pobranej w DetailView
#         context['comment_form'] = CommentForm()
#         return context

class SinglePostView(View):
    def is_saved_for_later(self, request, post_id):
        stored_posts = request.session.get('stored_posts')
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
        else:
            is_saved_for_later = False
        return is_saved_for_later


    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            'post': post,
            'tags': post.tags.all(),
            'comment_form': CommentForm(),
            'comments': post.comments.all().order_by('-id'),
            'saved_for_later': self.is_saved_for_later(request, post.id)
        }
        return render(request, 'blog/post-detail.html', context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)
        if comment_form.is_valid():
            comment = comment_form.save(
                commit=False)  # commit = False omija stworzenie recordu a zwraca insancje obiektu
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse('post-detail-page', args=[slug]))

        context = {
            'post': post,
            'tags': post.tags.all(),
            'comment_form': comment_form,
            'comments': post.comments.all().order_by('-id'),
            'saved_for_later': self.is_saved_for_later(request, post.id)
        }
        return render(request, 'blog/post-detail.html', context)


class ReadLaterView(View):
    def get(self, request):
        stored_post = request.session.get("stored_posts")
        context = {}

        if stored_post is None or len(stored_post) == 0:
            context["posts"] = []
            context['has_post'] = False
        else:
            posts = Post.objects.filter(id__in=stored_post)
            context["posts"] = posts
            context['has_post'] = True

        return render(request, 'blog/stored-posts.html', context)

    def post(self, request):
        stored_post = request.session.get("stored_posts")

        if stored_post is None:
            stored_post = []

        post_id = int(request.POST["post_id"])
        if post_id not in stored_post:
            stored_post.append(post_id)
            request.session['stored_posts'] = stored_post
        else:
            stored_post.remove(post_id)
            request.session['stored_posts'] = stored_post

        return HttpResponseRedirect('/')
