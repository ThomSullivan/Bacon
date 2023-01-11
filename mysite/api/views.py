from routes.models import Person, Movie, Step, Fav
from forum.models import Article, Comment
from home.models import Profile
from .serializers import UserProfileSerializer,  ArticleListSerializer, ArticleDetailSerializer, ArticlePostSerializer, CommentAddSerializer,CommentDeleteSerializer, ChampionViewSerializer, TopTenSerializer
from .permissions import IsCommentOwner
from routes.views import get_person_info, get_movie_info
from mysite.settings import TMDB_API_KEY

import requests

from django.shortcuts import  get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseRedirect, response
from django.urls import reverse, resolve
from django.db.models import Count

from rest_framework import generics, response, viewsets
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser

#Util functions
def search_pk(str):
        search = 'https://api.themoviedb.org/3/search/person?api_key={}&query={}'.format(TMDB_API_KEY, str)
        address = requests.get(search, params=str)
        object = address.json()
        try:
            person_id = object['results'][0]['id']
        except:
            HttpResponseBadRequest
        if person_id == 4724:
            return JsonResponse({'message':'You found secret bacon!'})
        try:
            x = Person.objects.get(name=person_id)
        except:
            #This grabs the first person is many people are returned
            try:
                x = Person.objects.filter(name=person_id)[0]
            except:
                #Error handling for someone not in the local DB
                return HttpResponseBadRequest
        return x.pk

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

class ResultDetailView(viewsets.ViewSet):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Step.objects.filter(pk=1)

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated] 
        return[permission() for permission in permission_classes]

    

    def list(self, request):
        pk = search_pk(request.data['name'])
        ctx = {'degrees':[], 'pk' : pk, 'title':[]}
        bacon = False
        person_id = pk
        while bacon == False:
            try:
                x = Person.objects.get(pk=person_id)
            except:
                return HttpResponseNotFound()
            # x is not a person object
            #checking for a local stored name and getting one if not
            if x.real_name == '':
                q = x.name
                info = get_person_info(q)
                x.real_name = info[0]
                x.img_path = info[1]
                x.save()
            # get a step object as y using x object as a parameter
            person = (x.id, x.name, x.real_name, x.img_path,x.bacon_number)
            ctx['title'].append(x.real_name)
            y = Step.objects.get(person=x)
            if y.movie.real_title == '':
                q = y.movie.title
                info = get_movie_info(q)
                y.movie.real_title = info[0]
                y.movie.img_path = info[1]
                y.movie.save()
            movie = (y.movie.title, y.movie.real_title, y.movie.img_path)
            ctx['degrees'].append((person, movie))
            if y.next_step.name == 4724:
                bacon = True
            else:
                person_id = y.next_step.id
        #check to see for favorite status
        favorites = list()
        if request.user.is_authenticated:
            ctx['favorite'] = False
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_people.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ int(row['id']) for row in rows ]
            if favorites.count(int(pk)) > 0:
                ctx['favorite'] = True
            current = Person.objects.get(id=pk)
            profile = Profile.objects.get(user=request.user.id)
            if current.bacon_number > profile.longest:
                profile.longest = current.bacon_number
                profile.save()
                ctx['record']=True
        return JsonResponse(ctx)
    
    def patch(self, request):
        pk = search_pk(request.data['name'])
        person = get_object_or_404(Person, pk=pk)
        try:
            fav = Fav.objects.get(user=request.user, person=person).delete()
        except:
            Fav.objects.create(user=request.user, person=person)
            return HttpResponse(status=201)
        return HttpResponse(status=201)
