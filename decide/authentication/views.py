from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist

from .serializers import UserSerializer
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404, HttpResponseRedirect

from .forms import UserCreateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout, login
from django.contrib.auth.decorators import login_required

from rest_framework import parsers, renderers
from rest_framework.authtoken.models import Token
from .serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from .schemas import ManualSchema
from rest_framework.views import APIView

from base import mods
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncYear

from django.shortcuts import render
from datetime import date,  timedelta

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.template import Context, loader
import ast

User=get_user_model()
    
class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)

class GetContadorView(APIView):
    def get(self,request):
        ##############################################################
        #  This method receives a request with tuple 'list'
        # 'list' value is a list of users id
        # This method returns a dictionary with keys:
        # 'man', 'woman','non-binary','total','minor', 'fullage' and 'all'
        # 'all' is a counter by gender group by year
        #############################################################
        id_list=[]
        #rcv   
           
        if request:
            id_list= request.GET.get('list', '[]')
        #id_list=['2','4','3','5']
        id_list=ast.literal_eval(id_list)
        id_list = list(map(int, id_list))

        #filtered users. In this way, we call only one time to db
        users = User.objects.filter(id__in=id_list)
        
        #count gender python    
        num_total=users.count()
        objectsM = users.filter(sex= User.SEX_OPTIONS[0][0]).count()
        objectsW = users.filter(sex=User.SEX_OPTIONS[1][0]).count()
        objectsN = users.filter(sex=User.SEX_OPTIONS[2][0]).count()

        #count age        
        today = date.today()
        age_legal = 18
        date_legal = date(today.year - age_legal - 1, today.month, today.day) + timedelta(days = 1)
        age_max=130
        date_max = date(today.year - age_max - 1, today.month, today.day) + timedelta(days = 1)
        objects_minor = users.filter(birthdate__range=(date_legal, today)).count()
        objects_fullage = users.filter(birthdate__range= (date_max, date_legal)).count()

        #count ( only 1 db). Grouping by date, and inside the date by gender
        
        queryset = User.objects.filter(id__in=id_list).annotate(
            date=TruncYear('birthdate'),
            ).values('date').annotate(
            total_entries=Count('id'),
            total_m=Count('id', filter=Q(sex=User.SEX_OPTIONS[0][0])),
            total_w=Count('id', filter=Q(sex=User.SEX_OPTIONS[1][0])),
            total_n=Count('id', filter=Q(sex=User.SEX_OPTIONS[2][0])),
            )
        queryset=list(queryset)
        
        #return
        data = { 'man' : objectsM,
        'woman' : objectsW,
        'non-binary' : objectsN, 
        'total' : num_total,
        'minor' : objects_minor,
        'fullage' : objects_fullage,
        'all' : queryset
        }
    
        return Response({'data': data})

class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
            logout(request)
        except ObjectDoesNotExist:
            pass

        return Response({})

class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({'token': token.key})

class ObtainAuthTokenRRSS(APIView):  
    def get(self, request, *args, **kwarsg):
        if(((request.session.has_key('google-oauth2_state')) or 
            (request.session.has_key('github_state')) or 
            (request.session.has_key('facebook_state'))) and
            (request.session.has_key('_auth_user_id'))):
            user = User.objects.get(pk=request.session['_auth_user_id'])
            token, created = Token.objects.get_or_create(user=user)
            request.session['auth-token'] = token.key
        return HttpResponseRedirect(request.GET.get('next', '/'))

obtain_auth_token_rrss = ObtainAuthTokenRRSS.as_view()

obtain_auth_token = ObtainAuthToken.as_view()

def signUp(request):
    if request.method == 'POST':
        formulario = UserCreateForm(request.POST)
        if formulario.is_valid():
            user=formulario.save(commit=False)
            user.is_active = False
            user.save()

            # Send an email to the user with the token:
            mail_subject = 'Activate your account.'
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = account_activation_token.make_token(user)
            activation_link = "http://{0}/authentication/activate/?uid={1}&token={2}".format(current_site, uid, token)
            message = "Thanks you for joining,\n You need to check this link to activate your account:\n {0} \n Best regards. \n Ganímedes team.".format(activation_link)
            
            to_email = formulario.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            # template = loader.get_template("authentication/confirm_email.html")
            return render(request, "authentication/confirm_email.html")

    else:
        formulario = UserCreateForm()
    return render(request, 'authentication/signup.html', {'formulario':formulario})

class Activate(APIView):
    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user:
            user.is_active = True
            user.save()
            # template = loader.get_template("authentication/acc_active_email.html")
            return render(request, "authentication/acc_active_email.html")


        else:
            return HttpResponse('Activation link is invalid!')

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # Important, to update the session with the new password
            return HttpResponse('Password changed successfully')
            
def form_login(request):
    return render(request, 'authentication/login.html')
