import requests

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from mysite.settings import TMDB_API_KEY
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from home.models import Profile
from .owner import OwnerDetailView
from .models import Step, Person, Fav


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
        
        ctx = {'degrees':[], 'pk' : pk, 'title':[]}
        bacon = False
        person = Person.objects.get(pk=pk)  
        ctx['title'].append(person.real_name)

        ##GAME FEATURES
        if 'search' in request.GET:
            #Only does stuff if the request came from the search page
            person.number_of_searches += 1
            person.save()
            ctx['search'] = True

        ctx['number_of_searches'] = person.number_of_searches

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
            if person.bacon_number > profile.longest and 'search' in request.GET:
                #Sets a new user record if request came from search page
                profile.longest = person.bacon_number
                profile.save()
                ctx['record']=True

        ##ROUTE FINDING
        while bacon == False:
            y = Step.objects.filter(person=person)[0]
            #Human readable names are filled as they are searched to save DB space
            if y.person.real_name == '':
                info = get_person_info(y.person.name)
                y.person.real_name, y.person.img_path = info[0], info[1]
                y.person.save()
            personInfo = (y.person.name, y.person.real_name, y.person.img_path, y.person.bacon_number)
            
            #Human readable names are filled as they are searched to save DB space
            if y.movie.real_title == '':
                info = get_movie_info(y.movie.title)
                y.movie.real_title, y.movie.img_path = info[0], info[1]
                y.movie.save()
            movie = (y.movie.title, y.movie.real_title, y.movie.img_path)
            ctx['degrees'].append((personInfo, movie))
            if y.next_step.name != 4724:
                person = y.next_step
                continue
            bacon = True

        

        

        return render(request, self.template_name, ctx)

def search_pk(request):
    search = 'https://api.themoviedb.org/3/search/person?api_key={}&query={}'.format(TMDB_API_KEY, request.GET['search'])
    address = requests.get(search, params=request.GET)
    object = address.json()
    try:
        person_id = object['results'][0]['id']
    except:
        return redirect('/?error=True')
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
            return redirect('/?error=True')
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
