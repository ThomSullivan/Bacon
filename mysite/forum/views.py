from .models import Article, Comment
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from routes.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

class ArticleListView(OwnerListView):
    model = Article
    # By convention:
    # template_name = "myarts/article_list.html"


class ArticleDetailView(OwnerDetailView):
    model = Article
    def get(self, request, pk) :
        x = Article.objects.get(id=pk)
        comments = Comment.objects.filter(article=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'article' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, 'forum/article_detail.html', context)


class ArticleCreateView(OwnerCreateView):
    model = Article
    fields = ['title', 'text']


class ArticleUpdateView(OwnerUpdateView):
    model = Article
    fields = ['title', 'text']


class ArticleDeleteView(OwnerDeleteView):
    model = Article


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Article, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, article=f)
        comment.save()
        return redirect(reverse('forum:article_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "forum/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        article = self.object.article
        return reverse('forum:article_detail', args=[article.id])