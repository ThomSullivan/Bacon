from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
import requests
from mysite.settings import TMDB_API_KEY
from .models import Step, Person, Movie, Fav
# Create your views here.
from django.views import View
from django.views.generic import DetailView
from .owner import OwnerDetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from home.models import Profile
from django.contrib.auth.models import User

def get_person_info(name):
    details = 'https://api.themoviedb.org/3/person/{}?api_key={}'.format(name, TMDB_API_KEY)
    details = requests.get(details)
    instance = details.json()
    info = (instance['name'], instance['profile_path'])
    return info

def get_movie_info(title):
    details = 'https://api.themoviedb.org/3/movie/{}?api_key={}'.format(title, TMDB_API_KEY)
    details = requests.get(details)
    instance = details.json()
    info = (instance['title'],instance['poster_path'])
    return info



class ResultDetailView(OwnerDetailView):
    model = Person
    template_name = 'routes/results.html'
    def get(self, request, pk):
        ##ROUTE FINDING
        ctx = {'degrees':[], 'pk' : pk, 'title':[]}
        bacon = False
        person_id = pk
        while bacon == False:
            x = Person.objects.get(pk=person_id)
            #Human readable names are filled as they are searched to save DB space
            if x.real_name == '':
                info = get_person_info(x.name)
                x.real_name, x.img_path = info[0], info[1]
                x.save()
            # get a step object as y using x object as a parameter
            person = (x.name, x.real_name, x.img_path,x.bacon_number)
            y = Step.objects.get(person=x)
            movie = Movie.objects.get(pk=y.movie.id)
            #Human readable names are filled as they are searched to save DB space
            if movie.real_title == '':
                info = get_movie_info(y.movie.title)
                movie.real_title, movie.img_path = info[0], info[1]
                movie.save()
            movie = (movie.title, movie.real_title, movie.img_path)
            ctx['degrees'].append((person, movie))

            if y.next_step.name != 4724:
                person_id = y.next_step.id
                continue
            bacon = True

        searched_person = Person.objects.get(pk=pk)  
        ctx['title'].append(searched_person.real_name)
        ctx['number_of_searches'] = searched_person.number_of_searches

        ##GAME FEATURES
        if 'search' in request.GET:
            #Only does stuff if the request came from the search page
            searched_person.number_of_searches += 1
            searched_person.save()
            ctx['search'] = True
        
        ##USER OPERATIONS
        #check to see for favorite status
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_people.values('pk')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['pk'] for row in rows ]
            ctx['favorites'] = favorites

            profile = Profile.objects.get(user=request.user.id)
            if searched_person.bacon_number > profile.longest and 'search' in request.GET:
                #Sets a new user record if request came from search page
                profile.longest = searched_person.bacon_number
                profile.save()
                ctx['record']=True

        return render(request, self.template_name, ctx)

def search_pk(request):
    search = 'https://api.themoviedb.org/3/search/person?api_key={}&query={}'.format(TMDB_API_KEY, request.GET['search'])
    address = requests.get(search, params=request.GET)
    object = address.json()
    try:
        person_id = object['results'][0]['id']
    except:
        ctx = {'error':True}
        return render(request, 'home/home.html', ctx)
    if person_id == 4724:
        return redirect('/routes/bacon')
    try:
        x = Person.objects.get(name=person_id)
    except:
        #This grabs the first person is many people are returned
        try:
            x = Person.objects.filter(name=person_id)[0]
        except:
            #Error handling for someone not in the local DB
            ctx = {'error':True}
            return render(request, 'home/home.html', ctx)
    parameter = x.pk

    return redirect('/routes/result/' + str(parameter)+'?search=True')

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Person, id=pk)
        fav = Fav(user=request.user, person=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Person, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, person=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
