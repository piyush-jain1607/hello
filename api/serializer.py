from rest_framework import serializers
from django.contrib.auth.models import  Group , Permission
from django.contrib.auth import get_user_model
from .models import Post
User = get_user_model()


class PermissionSerializer (serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields ='__all__'

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many = True , read_only = True)
    class Meta :
        model = Group
        fields = ('name','permissions')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many = True , read_only = True)
    user_permissions = PermissionSerializer(many = True , read_only = True)
    class Meta :
        model = User
        fields = ('username','email','password','groups','user_permissions')
        extra_kwargs = {'password' : {'write_only' : True ,'min_length' : 8}}



class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'