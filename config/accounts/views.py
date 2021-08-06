from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.models import User #회원가입을 구현하는데 있어 장고가 제공해주는 편리함
from django.urls import reverse
from django.contrib import auth
from django.views import View
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from . import forms
# Create your views here.

def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:
            user = User.objects.create_user(
                username=request.POST["username"], password=request.POST["password1"])
            auth.login(request, user)
            print("회원가입 성공!")
            return redirect('/accounts/') #home 페이지 따로 만들어야 댐! url 이름이 home 이어야 댐!
        return render(request, 'accounts/signup.html')
    #실패시 안넘어감
    return render(request, 'accounts/signup.html')

# def login(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         print("username:", username)
#         user = auth.authenticate(request, username=username, password=password)
#         print("!!!")
#         print("user:", user)
#         if user is not None:
#             auth.login(request, user)
#             print("???")
#             return redirect('/accounts/')
#         else:#실패시
#             print("@@@@")
#             return render(request, 'accounts/login.html', {'error': 'username or password is incorrect'}) #에러 메시지가 출력이 안됨,,,
#     else:
#         print("로그인 성공!")
#         return render(request, 'accounts/login.html')

class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        ctx = {
            "form": form,
        }
        return render(request, "accounts/login.html", ctx)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, "accounts/home.html")

        return render(request, "accounts/login.html", {"form": form})

@login_required
def logout(request):
    django_logout(request)
    return render(request, "accounts/main.html")

def main(request):
    return render(request, 'accounts/main.html')

def home(request):
    return render(request, 'accounts/home.html')




#인자를 받아와서
# def detail(request, blog_id):
#     print("detail!")
#     blog_detail = get_object_or_404(Blog, pk=blog_id) #첫번째 클래스의 두번째 항목 pk값에 해당하는 것만 가져옴
#     return render(request, 'accounts/detail.html', {'blog': blog_detail})

# def new(request):
#     return render(request, 'accounts/new.html')

# #정보를 DB에 저장하는
# def create(request):
#     blog = Blog() #객체 생성
#     blog.title = request.GET['title'] #각각의 정보 저장
#     blog.body = request.GET['body']
#     blog.pub_date = timezone.datetime.now()
#     blog.save() #db에 저장
#     #redirect 에러 나는중,,,,
#     return redirect('http://127.0.0.1:8000/accounts/blog/'+str(blog.id)) #url은 항상 str이어야 한다 기존 int형을 형변환

#render : html에 파이썬 다른 변수 넘겨줄 수 있음
#redirect : 외부 url 입력할 수 있다