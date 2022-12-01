from django.db import models
from django.conf import settings
# Create your models here.
bacon_id = 4724

class Person(models.Model):
    name = models.IntegerField()
    real_name = models.CharField(max_length=100, default='')
    img_path = models.CharField(max_length=100, default='', null=True)
    bacon_number = models.IntegerField(null=True, default='3')
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Fav', related_name='favorite_people')

class Movie(models.Model):
    title = models.IntegerField()
    real_title = models.CharField(max_length=100, default='')
    img_path = models.CharField(max_length=100, default='', null=True)

class Step(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    next_step = models.ForeignKey(Person, on_delete=models.CASCADE,related_name='next_step_person',default=bacon_id)

class Fav(models.Model) :

    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favs_users')

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('person', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.person.name[:10])