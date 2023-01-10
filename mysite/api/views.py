from routes.models import Person, Movie, Step, Fav
from forum.models import Article, Comment
from home.models import Profile
from .serializers import UserProfileSerializer,  ArticleListSerializer, ArticleDetailSerializer, ArticlePostSerializer, CommentAddSerializer,CommentDeleteSerializer, ChampionViewSerializer, TopTenSerializer
from .permissions import IsCommentOwner
from routes.views import get_person_info

from django.shortcuts import  get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseRedirect, response
from django.urls import reverse, resolve
from django.db.models import Count

from rest_framework import generics, response, viewsets
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Create your views here.

class UserProfileView(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    ordering_fields = ['id']

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.filter(user=user).order_by('id')
        return profile

class ArticleListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleListSerializer
    queryset = Article.objects.all().order_by('id')
    search_fields = ['title','text','owner_id__username'] 

    def get_serializer_class(self):
        serializer_class = ArticleListSerializer
        if self.request.method == 'POST':
            serializer_class = ArticlePostSerializer
        return serializer_class

class ArticleDetailView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ArticleDetailSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsCommentOwner | IsAdminUser ] 
        return[permission() for permission in permission_classes]

    def get_queryset(self):
        query = Article.objects.filter(pk=self.kwargs['pk']).order_by('id')
        return query
    
    def post(self, request, *args, **kwargs):
        serialized_item = CommentAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        pk = self.kwargs['pk']
        article = Article.objects.get(pk=pk)
        text = request.data['text']
        Comment.objects.create(article=article, owner=request.user, text=text)
        return JsonResponse(status=201, data={'message':'The comment was posted'}) 
    
    def delete(self, request, *args, **kwargs):
        serialized_item = CommentDeleteSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        comment = get_object_or_404(Comment, pk=self.request.data['id'])
        comment.delete()
        return JsonResponse(status=204, data={'message':'The comment was deleted'})

class ChampionsView(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ChampionViewSerializer
    queryset = Profile.objects.all().order_by('-longest')[:10]

class TopTenView(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = TopTenSerializer
    queryset = Person.objects.annotate(fav_count=Count('favorites')).order_by('-fav_count')[:10]

class StatisticsView(viewsets.ViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Step.objects.filter(pk=1)
    def list(self, request):
        total = Person.objects.count()
        q = Step.objects.values('next_step').annotate(c=Count('next_step')).order_by('-c').exclude(next_step=2469)[:10]
        ten_list = []
        for item in q:
            x = Person.objects.get(id=item['next_step'])
            if x.real_name == '':
                info = get_person_info(x.name)
                x.real_name = info[0]
                x.img_path = info[1]
                x.save()
            ten_list.append((x.real_name, x.img_path, item['c']))
        q = Person.objects.values('bacon_number').annotate(c=Count('bacon_number'))
        ctx = {'total':total, 'ten_list':ten_list, 'bacon_numbers':[x for x in q]}
        return JsonResponse(ctx)


