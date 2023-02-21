import hashlib
import urllib
import requests
import json

import stripe

from mysite.settings import TMDB_API_KEY, CONTACT_EMAIL, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from .models import Profile
from .forms import contactMeForm
from routes.views import get_person_info
from routes.models import Person, Step

from django import template
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from routes.owner import OwnerDetailView
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

register = template.Library()

class ProfileDetailVeiw(OwnerDetailView):
    model = User
    template_name = 'home/profile.html'
    def get(self, request, pk):

        user = User.objects.get(id=pk)
        fav_people_objects = [person for person in user.favorite_people.all()]
        fav_people_list = []
        for object in fav_people_objects:
            url = 'https://api.themoviedb.org/3/person/{}?api_key={}'.format(object.name, TMDB_API_KEY)
            details = requests.get(url, params=request.GET)
            instance = details.json()
            fav_people_list.append((instance['name'],object.id))
        profile = Profile.objects.get(user=user)
        ctx = {'user_profile':user,'profile':profile, 'favs':fav_people_list}
        return render(request, self.template_name, ctx)

def homeView(self):
   
    return render(self, 'home/home.html')


def contactMe(request):
    if request.method == 'POST':
        form = contactMeForm(request.POST)
        if form.is_valid():
            subject = 'Someone sent an e-mail from Six Degrees'
            message = f"name: {form.cleaned_data['name']}\nE-mail Address: {form.cleaned_data['emailAddress']}\nMessage:\n{form.cleaned_data['message']}"
            send_mail(
                subject,
                message,
                None,
                [CONTACT_EMAIL]
            )
            messages.add_message(request, messages.SUCCESS, 'Your Message has been sent!')
            return HttpResponseRedirect('/')
    else:
        form = contactMeForm()
    return render(request, 'home/contactMe.html', {'form':form})

def accountManageView(self):
    return render(self, 'home/manage.html')

def top_ten(self):
    q1 = Person.objects.annotate(fav_count=Count('favorites'))
    q1 = q1.order_by('-fav_count')[:10]
    ctx = {'person_list' : [] }
    counter = 1
    for x in q1:
        if x.real_name == '':
            q = x.name
            info = get_person_info(q)
            x.real_name = info[0]
            x.img_path = info[1]
            x.save()

        ctx['person_list'].append((x.real_name,x.img_path,x.id,counter))
        counter+=1
    return render(self, 'home/topten.html', ctx)

def statistics(self):
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
        ten_list.append((x.real_name, x.img_path, x.id, item['c']))
    q = Person.objects.values('bacon_number').annotate(c=Count('bacon_number')).order_by('bacon_number')
    ctx = {'total':total, 'ten_list':ten_list, 'bacon_numbers':q}
    return render(self, 'home/statistics.html', ctx)

def champions(self):
    q = Profile.objects.all()
    q = q.order_by('-longest')[:10]
    ctx = {'champ_list':[]}
    for item in q:
        ctx['champ_list'].append((item.user, item.longest))
    return render(self, 'home/champions.html', ctx)

####Stripe functionality and settings###
stripe.api_key = STRIPE_SECRET_KEY

def donate(request):
    return render(request, 'home/donate.html')

@method_decorator(csrf_exempt)
def create_payment(request):
    if request.method == 'POST':
        metadata = {}
        if request.user.is_authenticated:
            metadata['user'] = request.user
            
        data = json.loads(request.body.decode('utf8'))
        metadata['item'] = data['item']
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=500,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,  
            },
            description = f"{metadata['item']} donation",
            metadata = metadata
        )
        
        return JsonResponse({
            'clientSecret': intent['client_secret']
        })
    
@method_decorator(csrf_exempt)
def stripe_webhook(request):
    event = None
    payload = request.body.decode('utf8')
    
    try:
        event = json.loads(payload)
        print (json.dumps(event, indent=3))
    except:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return HttpResponse(status=400)
    if STRIPE_WEBHOOK_SECRET:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return HttpResponse(status=400)
        # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_intent['amount']))
        
    elif event['type'] =='charge.succeeded':
        eventObject = event['data']['object']
        message = 'You most generous donation of $5 will help my servers stay running for another month.'
        if eventObject['metadata']['item'] == 'Coffee':
            message = 'I love coffee so very much and appreciate you buying me a cup.'
        wholeMessage = f"{message}\nYour receipt can found here:\n{eventObject['receipt_url']}\nThank you so much!\n\n\nThomas"
        send_mail(
                f'Thank you for donating!!',
                wholeMessage,
                None,
                [CONTACT_EMAIL]
            )
        pass
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)
    
def donate_success(request):
    
    if request.GET:
        messages.add_message(request, messages.SUCCESS, 'Your donation has been recieved')
    
    return render(request, 'home/donate_success.html')


# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
  default = "https://example.com/static/images/defaultavatar.jpg"
  return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d':default, 's':str(size)}))

# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s" width="%d" height="%d">' % (url, size, size))