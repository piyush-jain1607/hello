from json import JSONDecodeError
import json, jwt, redis
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from api.models import Post
from .serializer import (GroupSerializer, PermissionSerializer, PostSerializer, UserSerializer)
from .utils import generate_access_token, generate_refresh_token

User = get_user_model()
redis = redis.Redis(host='localhost', port=6379, db=0)
# Create your views here.

ct = ContentType.objects.get_for_model(Post)


def Message(err):
    return Response({"status": 400, "data": {"message": err}})


@api_view(['GET'])
@permission_classes([AllowAny])
def apiOverView(req):
    urls = {
        'login': 'Login User',
        'signup': 'Signup User'
    }
    return Response(urls)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(req):
    try:
        body = json.loads(req.body)
        username = body['username']
        password = body['password']
        email = body['email']
        user = User.objects.create_user(username=username, email=email, password=password)
        print(user)
        return Response("user created successfully")
    except:
        print("error")
        return Response("user with same credentials exist")


@api_view(['POST'])
@permission_classes([AllowAny])
def userLogin(request):
    body = json.loads(request.body)
    email = body['email']
    password = body['password']
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return Message("Login Successful")
    else:
        return Message("Login Failed")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPosts(req):
    user = req.user
    if user is not None:
        posts = user.post_set.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    return Message("Token expired")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addPost(req):
    try:
        body = json.loads(req.body)
        print(req.body)
        post = req.user.post_set.create(author=req.user, title=body['title'])
        post.save()
        return Response({"username": req.user.username})
    except:
        raise exceptions.ParseError("not valid data")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @csrf_exempt
def getGroups(req):
    grps = Group.objects.all()
    serializer = GroupSerializer(grps, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getGroup(req, name):
    group = Group.objects.get(name=name)
    serializer = GroupSerializer(group)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUsers(req):
    users = User.objects.order_by("-username")
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def getUserByEmail(req):
    if req.method == 'POST':
        try:
            body = json.loads(req.body)
            user = User.objects.get(email=body['email'])
            seri = UserSerializer(user)
            return Response(seri.data)
        except (User.DoesNotExist, JSONDecodeError):
            return Message("No user with such email address exists")

    else:
        try:
            body = json.loads(req.body)
            user = User.objects.get(email=body['email'])
            user.email = body['new-email']
            user.save()
            seri = UserSerializer(user)
            return Response(seri.data)
        except (User.DoesNotExist, JSONDecodeError):
            return Message("Provide a new email address")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPermissions(req):
    permissions = Permission.objects.all()
    serializer = PermissionSerializer(permissions, many=True)
    print(permissions)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPermission(req):
    try:
        body = json.loads(req.body)
        permission = Permission.objects.create(codename=body['codename'], name=body['name'], content_type=ct)
        permission.save()
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    except:
        return Response("Duplicate Permissions")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def groupPermissions(req, name, id):
    try:
        grp = Group.objects.get(name=name)
        perm = Permission.objects.get(id=id)
        if req.method == 'POST':
            grp.permissions.add(perm)
            grp.save()
        serializer = GroupSerializer(grp)
        return Response(serializer.data)
    except:
        return Response("an error occurred")


@api_view(['POST'])
def addUserPermission(req, username, pid):
    try:
        user = User.objects.get(username=username)
        if req.method == 'POST':
            permission = Permission.objects.get(id=pid)
            user.user_permissions.add(permission)
            user.save()
        return Response(UserSerializer(user).data)
    except:
        return Message("An error occured")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GroupPerms(req, name):
    try:
        grp = Group.objects.get(name=name)
        serializer = GroupSerializer(grp)
        return Response({"data": serializer.data.get("permissions"), "user": req.user.username})
    except:
        return Message("An error occured")


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    response = Response()
    if (email is None) or (password is None):
        raise exceptions.AuthenticationFailed('email and password required')

    user = User.objects.filter(email=email).first()
    if user is None:
        raise exceptions.AuthenticationFailed('user not found')
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('wrong password')

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    redis.sadd('outs', access_token)
    response.data = {
        'access': access_token,
        'refresh': refresh_token
    }

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def refresh_token_view(request):
    refresh_token = request.data.get('refresh')

    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        if redis.sismember('cbl', refresh_token):
            raise exceptions.AuthenticationFailed('Blacklisted refresh Token')

        payload = jwt.decode(
            refresh_token, bytes(settings.PBKEY, 'utf-8'), algorithms=['RS256'])

    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')
    if payload["token_type"] == "access":
        raise exceptions.NotAcceptable("Access tokens not supported")

    user = User.objects.filter(email=payload.get('user_email')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = generate_access_token(user)
    new_ref_token = generate_refresh_token(user)

    redis.sadd('cbl', refresh_token)
    redis.sadd('outs', access_token)
    return Response(
        {'refresh': new_ref_token,
         'access': access_token
         }
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createGroup(req):
    try:
        body = json.loads(req.body)
        try:
            grp = Group.objects.create(name=body['name'])
            grp.save()
        except:
            return Message("duplicate group name")
        serializer = GroupSerializer(grp)
        return Response(serializer.data)
    except:
        raise exceptions.NotAcceptable("Invalid Request data")
