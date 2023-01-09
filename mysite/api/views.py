from routes.models import Person, Movie, Step, Fav
from forum.models import Article, Comment
from home.models import Profile
from .serializers import UserProfileSerializer, UserFavoritesSerializer, ArticleListSerializer, ArticleDetailSerializer, ArticlePostSerializer, CommentAddSerializer

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.urls import reverse, resolve

from rest_framework import generics
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

class UserFavoritesView(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoritesSerializer

    def get_queryset(self):
        favorites = self.request.user.favorite_people.all()
        return favorites

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
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleDetailSerializer

    def get_queryset(self):
        query = Article.objects.filter(id=self.kwargs['pk'])
        return query
    
    def post(self, request, *args, **kwargs):
        serialized_item = CommentAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        pk = self.kwargs['pk']
        article = Article.objects.get(pk=pk)
        text = request.data['text']
        
        Comment.objects.create(article=article, owner=request.user, text=text)
        
        return JsonResponse(status=201, data={'message':'Comment posted!'})