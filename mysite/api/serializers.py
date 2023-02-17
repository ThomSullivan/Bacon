from routes.models import Person, Movie, Step, Fav
from forum.models import Article, Comment
from home.models import Profile

from rest_framework import serializers
from django.contrib.auth.models import User

class OwnerSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class UsernameHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class UserProfileSerializer(serializers.ModelSerializer):
    def get_favorites(self, obj):
        favorites = Person.objects.filter(favorites=obj.id)
        favorites = favorites.values()
        return favorites
    favorites = serializers.SerializerMethodField('get_favorites')
    user = UsernameHelperSerializer()
    class Meta():
        model = Profile
        fields = ['id','user','longest','favorite_bacon','favorites']

class ArticlePostSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(),
    default=serializers.CurrentUserDefault()
    )
    class Meta():
        model = Article
        fields = ['title','text','owner']
        extra_kwargs = {
            'text': {'min_length': 10},
            'title': {'min_length': 5},
        }

class ArticlePutSerializer(serializers.ModelSerializer):  
    class Meta():
        model = Article
        fields = ['title','text']

class ArticleListSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()
    class Meta():
        model = Article
        fields = ['id','title','owner']
        

class ArticleDetailHelperSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()
    class Meta():
        model = Comment
        fields = ['id','owner','text']


class ArticleDetailSerializer(serializers.ModelSerializer):
    def get_comments(self, obj):
        comments = Comment.objects.filter(article=obj.id).order_by('-updated_at')
        comments = comments.values('id','text','owner__username', 'created_at')
        return comments

    comments = serializers.SerializerMethodField('get_comments')
    owner = OwnerSerializer()
    class Meta():
        model = Article
        fields = ['owner','title','text','comments']

class CommentAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = Comment
        fields = ['text']
        extra_kwargs = {
            'text': {'min_length': 1},
        }
    
class CommentDeleteSerializer(serializers.ModelSerializer):
    class Meta():
        model = Comment
        fields = ['id']

class ChampionViewSerializer(serializers.ModelSerializer):
    def get_username(self, obj):
        user = User.objects.get(pk=obj.user.id)
        return user.username
    user = serializers.SerializerMethodField('get_username')
    class Meta():
        model = Profile
        fields = ['user','longest']

class TopTenSerializer(serializers.ModelSerializer):
    class Meta():
        model = Person
        fields = ['real_name','favorites']

