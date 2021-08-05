from django.urls import path
from rango import views

app_name='rango'

urlpatterns=[
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('category/<slug:category_name_slug>/',views.show_category,name='show_category'),
    path('add_category/',views.add_category,name='add_category'),
    path('category/<slug:category_name_slug>/add_page/',views.add_page,name='add_page'),
    path('page/add_like_number/', views.add_like_number, name='add_like_number'),
    path('page/sub_like_number/', views.sub_like_number, name='sub_like_number'),
    path('restricted/',views.restricted,name='restricted'),
    path('category/<slug:category_name_slug>/comment/',views.comment,name='comment'),
    path('search/', views.search, name='search'),
    path('profile/<str:userName>/',views.profile,name='profile'),
]