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
    user = UsernameHelperSerializer()
    class Meta():
        model = Profile
        fields = '__all__'

class UserFavoritesSerializer(serializers.ModelSerializer):
    class Meta():
        model = Person
        fields = ['name','real_name']

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

class ArticleListSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()
    class Meta():
        model = Article
        fields = ['id','title','owner']
        

class ArticleDetailHelperSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()
    class Meta():
        model = Comment
        fields = ['owner','text']


class ArticleDetailSerializer(serializers.ModelSerializer):
    def get_comments(self, obj):
        comments = Comment.objects.filter(article=obj.id).order_by('-updated_at')
        comments = comments.values('text','owner__username', 'created_at')
        print(comments)
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
    
   