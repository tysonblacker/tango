from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from random import randint
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


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
    contest_dict['cat_list'] = get_category_list()
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

    return render_to_response('rango/category.html', context_dict, context)

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

def get_category_list():
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


def search(request):
    context = RequestContext(request)
    result_list = []
 
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render_to_response('rango/search.html', {'result_list': result_list}, context)
