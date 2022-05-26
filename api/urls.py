from django.urls import path
from . import views

urlpatterns = [
    path('', views.apiOverView, name='API OVERVIEW'),
    path('posts/', views.getPosts, name='get posts by a user'),
    path('posts/add/', views.addPost, name='add user post'),
    path('users/', views.getUsers, name='All Users'),
    path('users/login/', views.userLogin, name="Login"),
    path('users/signup/', views.register, name='SignUp'),
    path('users/byid/', views.getUserByEmail, name='byid'),
    path('token/', views.login_view, name='token_obtain_pair'),
    path('groups/create/', views.createGroup, name=' hello new grp'),
    path('token/refresh/', views.refresh_token_view, name='token_refresh'),
    path('users/<str:username>/permissions/<int:pid>/', views.addUserPermission, name='add user permission'),
    path('groups/<str:name>/', views.getGroup, name='Group by name'),
    path('groups/<str:name>/permissions/<int:id>', views.groupPermissions, name='Group by name'),
    path('groups/<str:name>/permissions/', views.GroupPerms, name='add user permission'),
    path('groups/', views.getGroups, name='All groups'),
    path('permissions/', views.getPermissions, name='get all permissions'),
    path('permissions/create/', views.createPermission, name='Add new permission'),
]
