from django.contrib.auth.models import User
from rango.models import Page,Comment,Category,UserProfile
from rango.forms import CategoryForm,UserForm, UserProfileForm,PageForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from django.shortcuts import render, get_object_or_404,redirect

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger,InvalidPage
from rango.bing_search import run_query
def index(request):
    category_list=Category.objects.order_by('-likes')[:5]
    page_list=Page.objects.order_by('-views')[:5]
    context_dict={}
    context_dict['boldmessage']='Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories']=category_list
    context_dict['pages']=page_list
    visitor_cookie_handler(request)
    response=render(request,'rango/index.html',context=context_dict)
    return response

def about(request):
    context_dict={}    
    visitor_cookie_handler(request)
    context_dict['visits']=request.session['visits']
    return render(request,'rango/about.html',context=context_dict)

def show_category(request,category_name_slug):
    context_dict={}
    try:
        category=Category.objects.get(slug=category_name_slug)
        pages=Page.objects.filter(category=category)
        context_dict['pages']=pages
        context_dict['category']=category
    except Category.DoesNotExist:
        context_dict['category']=None
        context_dict['pages']=None

    return render(request,'rango/category.html',context=context_dict)



@login_required
def add_category(request):
    form=CategoryForm()
    
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html',{'form':form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    if category is None:
        return redirect('/rango/')

    form=PageForm()

    if request.method=='POST':
        form=PageForm(request.POST)

        if form.is_valid():
            if category:
                page=form.save(commit=False)
                page.category=category
                page.views=0
                page.save()
                return redirect(reverse('rango:show_category',kwargs={'category_name_slug':category_name_slug}))    
        else:
            print(form.errors)   
    context_dict={'form':form,'category':category}
    return render(request,'rango/add_page.html',context=context_dict)

    
@login_required
def restricted(request):
    return render(request,'rango/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

def get_server_side_cookie(request,cookie,default_val=None):
    val=request.session.get(cookie)
    if not val:
        val=default_val
    return val

def visitor_cookie_handler(request):
    visits=int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie=get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time=datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now()-last_visit_time).days>0:
        visits=visits+1
        request.session['last_visit']=str(datetime.now())
    else:
        request.session['last_visit']=last_visit_cookie
    
    request.session['visits']=visits

@login_required
def comment(request,category_name_slug):
    context_dict={}
    category=Category.objects.get(slug=category_name_slug)
    if request.method == 'POST':
        text=request.POST.get('text')
        page=request.POST.get('pageChoosen')
        name=request.user.username
        comment=Comment.objects.create(name=name,text=text,category=category,page=page)
        comment.save()

    category=Category.objects.get(slug=category_name_slug)
    pages=Page.objects.filter(category=category)
    context_dict['pages']=pages
    context_dict['category']=category
    comment=Comment.objects.filter(category=category)
    context_dict['comment']=comment
    number=comment.count()
    context_dict['number']=number
    return render(request, 'rango/comment.html', context=context_dict)

def search(request):    
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
              result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def profile(request,userName):
    context_dict={}
    try:
        context_dict['userName']=userName

        loginUser=User.objects.filter(username=userName)
        userProfile=UserProfile.objects.filter(user=loginUser[0])
        context_dict['userProfile']=userProfile
        print(context_dict['userProfile'])

    except Category.DoesNotExist:
        context_dict['userName']=None
        context_dict['userProfile']=None
        print("except")

    return render(request, 'rango/profile.html', context=context_dict)

@login_required
def add_userProfile(request,userName):
    user=User.objects.get(username=userName)
    context_dict={}
    category_list=Category.objects.order_by('-likes')[:5]
    page_list=Page.objects.order_by('-views')[:5]
    context_dict['boldmessage']='Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories']=category_list
    context_dict['pages']=page_list

    if request.method == 'POST':
        try:
            userProfile=UserProfile.objects.get(user=user)
        except:
            userProfile=UserProfile.objects.create(user=user)
    userProfile.save()
    
    return render(request, 'rango/index.html',context=context_dict)

def add_like_number(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET['page_id']
    like = 0
    if page_id:
        page = Page.objects.get(id=int(page_id))
        if page:
            like = page.likeNumber + 1
            page.likeNumber = like
            page.save()

            currentUser = request.user
            theUser = UserProfile.objects.get(user=currentUser)
            theUser.likedPages.add(page)
            theUser.save()
    return HttpResponse(like)


def sub_like_number(request):
    page_id = None
    if request.method == 'GET':
        page_id = request.GET['page_id']
    like = 0
    if page_id:
        page = Page.objects.get(id=int(page_id))
        if page:
            like = page.likeNumber - 1
            page.likeNumber = like
            page.save()
    return HttpResponse(like)

def add_like_number_category(request,category_name_slug):
    cate_name = category_name_slug
    if cate_name:
        category = Category.objects.get(slug=cate_name)
        print(category.slug)
        currentUser = request.user
        theUser = UserProfile.objects.get(user=currentUser)
        liked = False
        for category1 in theUser.likedCategories.all():
            if category1.slug==cate_name:
                liked=True


        if not liked:
            print(category.slug)
            like = category.likes + 1
            category.likes = like
            category.save()

            
            theUser.likedCategories.add(category)
            theUser.save()

    context_dict={}
    category=Category.objects.get(slug=category_name_slug)
    pages=Page.objects.filter(category=category)
    context_dict['pages']=pages
    context_dict['category']=category

    return render(request,'rango/category.html',context=context_dict)


def sub_like_number_category(request,category_name_slug):
    cate_name = category_name_slug
    if cate_name:
        category = Category.objects.get(slug=cate_name)
        currentUser = request.user
        theUser = UserProfile.objects.get(user=currentUser)
        liked = False
        for category1 in theUser.likedCategories.all():
            if category1.slug==cate_name:
                liked=True


        if  liked:
            like = category.likes - 1
            category.likes = like
            category.save()
            

            theUser.likedCategories.remove(category)
            theUser.save()

    context_dict={}
    category=Category.objects.get(slug=category_name_slug)
    pages=Page.objects.filter(category=category)
    context_dict['pages']=pages
    context_dict['category']=category

    return render(request,'rango/category.html',context=context_dict)

def search(request):
    result_list = []
    query = ''

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
    
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})

