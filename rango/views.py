from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from random import randint
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query_global
from rango.cat_search import run_query, run_query_cat


def index(request):
    context = RequestContext(request)
    
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    context_dict['cat_list'] = get_category_list()
    #context_dict = {'boldmessage': "I am a bold font from the context"}
    for category in category_list:
        category.url = category.name.replace(' ','_')
    """ for page in page_list:
        page. = page.t.replace(' ','_') """

      
    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits',0)
        print last_visit_time
        print visits

        if (datetime.now() - datetime.strptime(last_visit_time[:-7],
                                               "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    return render_to_response('rango/index.html', context_dict, context)
 

def about(request):
    context = RequestContext(request)
    ##request.session.get('visits',0)
    image_name = "rango{0}.jpg".format(randint(1,3))
    context_dict = {'boldmessage': "blah blah blah", 'image_name': image_name, 
                    'visits': request.session.get('visits',0) }
    print context_dict
    context_dict['cat_list'] = get_category_list()
    return render_to_response('rango/about.html', context_dict, context)


def category(request, category_name_url):
    context = RequestContext(request)
    category_name = category_name_url.replace('_',' ')
    context_dict = {'category_name': category_name, 'category_name_url': category_name_url}
    context_dict['cat_list'] = get_category_list()
    
    

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query_global(query)
            context_dict['result_list'] = result_list


    return render_to_response('rango/category.html', context_dict, context)

@login_required
def like_category(request):
    context = RequestContext(request)
    print "liking category"
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    print cat_id    
    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()
 
    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list  = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list  = Category.objects.all()


    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
 
    for cat in cat_list:
        cat.url = encode_url(cat.name)

    print cat_list
    return cat_list

def suggest_category(request):
    context = RequestContext(request)
    print "getting suggestion"
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        print starts_with
   
    cat_list = get_category_list(3, starts_with)

    context_list = {'cat_list': cat_list}
    print context_list

    return render_to_response('rango/category_list.html', context_list, context)


@login_required
def add_category(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    cat_list = get_category_list()
    return render_to_response('rango/add_category.html',
                 {'form': form, 'cat_list': cat_list}, context)

def decode_url(url_name):
    return url_name.replace("_"," ")

def encode_url(url_name):
    return url_name.replace(" ","_")

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page  = form.save(commit=False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('/rango/add_catebgory.html',{}, context)

            page.views = 0
            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'category_name_url': category_name_url, 
                    'category_name': category_name,
                    'form': form,
                    'cat_list': get_category_list,
                   }

    return render_to_response('rango/add_page.html', 
             context_dict, context)
             
@login_required
def auto_add_page(request):
    print request
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        print "is GET"
        cat_id = request.GET['category_id']
        print cat_id
        url = request.GET['url']
        title = request.GET['title']
        print url
        print title
        if cat_id != 0:
            print "has Cat id"
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
 
    response = render_to_response('rango/page_list.html', context_dict, context)
    print response
    return response


def register(request):
        
    context = RequestContext(request)
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
             'rango/register.html',
             {'user_form': user_form, 'profile_form': profile_form,
              'registered':registered },
             context)


def user_login(request):
    context = RequestContext(request)
    context_dict = {}
    context_dict['bad_details'] = False
    context_dict['account_disabled'] = False
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user  = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else: 
                context_dict['account_disabled'] = True
                return render_to_response('rango/login.html', context_dict, context)

        else:
            print "Invalid login details: {0} {1}".format(username, password)
            context_dict['bad_details'] = True
            return render_to_response('rango/login.html', context_dict, context)
    else:
        return render_to_response('rango/login.html', context_dict, context)

def get_category_list_1():
    cat_list = Category.objects.all()

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list

@login_required
def restricted(request):
    return HttpResponse("Since you are logged in you can see this")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


def search_gobal(request):
    print "searching global now"
    context = RequestContext(request)
    result_list = []
 
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render_to_response('rango/global_search.html', 
                          {'result_list': result_list}, context)

def search_cat(request):
    print "searching cat now"
    context = RequestContext(request)
    result_list = []
 
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query_global(query)

    return render_to_response('rango/search.html', 
                          {'result_list': result_list}, context)

def search(request):
    print "searching now"
    context = RequestContext(request)
    result_list = []
 
    if request.method == 'POST':
        query = request.POST['query'].strip()
        print "query"
        if query:
            result_list = run_query_global(query)

    return render_to_response('rango/category.html', 
                          {'result_list': result_list}, context)


@login_required
def profile(request):
    context = RequestContext(request)
  
    user = User.objects.get(username=request.user)
    try:
        profile = UserProfile.objects.get(user=user)

    except:
        profile = None    

    print profile

    context_list = {'user': user}
    context_list['cat_list'] = get_category_list()
    context_list['user_profile'] = profile
    
    return render_to_response('rango/profile.html', context_list, context)
 

def track_url(request):
 
    context = RequestContext(request)
    
    page_id = None
    url = "/rango/"
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            print page_id
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
                   
        return redirect(url)      

def plain(request):
    context = RequestContext(request)

    return render_to_response('rango/plain.html',{} ,context)        
