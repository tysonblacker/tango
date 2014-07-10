from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User
from django import forms

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text=\
              "please enter the category name")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    
    class Meta:
        model = Category

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text=\
              "please enter the page title")
    url = forms.CharField(max_length=128, help_text=\
              "please enter the page url")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
 
    class Meta:
        model = Page
        fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
   
        if url and not url.startswith('http://'):
             url = "http://" + url
             cleaned_data['url'] = url
 
        return cleaned_data

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


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
            if 'picture' in request.FILES:
                user.save()
                registered = True

        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
                'rango/register.html',
                {'user_form': user_form, 'profile_form': profile_form, 
                 'registered': registered}, context)


