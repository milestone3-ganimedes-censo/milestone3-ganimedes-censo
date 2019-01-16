
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from base import mods
from .forms import *

import os

User=get_user_model()

class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(email='voter1@gmail.com')
        u.set_password('test1234')
        u.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'email': 'voter1@gmail.com', 'password': 'test1234'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'email': 'voter1', 'password': 'test1234'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'email': 'voter1@gmail.com', 'password': 'test1234'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['email'], 'voter1@gmail.com')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'email': 'voter1@gmail.com', 'password': 'test1234'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__email='voter1@gmail.com').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'email': 'voter1@gmail.com', 'password': 'test1234'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__email='voter1@gmail.com').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__email='voter1@gmail.com').count(), 0)

#------------------------nuevo-usuario------------------------------
#sudo python3 ./manage.py test authentication.tests
    
    #new user
    def test_nuevo_usuario_ok(self):
        os.environ['NORECAPTCHA_TESTING'] = 'True'

        data = {'email': 'new1@mail.com', 'first_name': 'new', 'last_name': 'new', 'birthday':'01/01/2000', 'password1': 'practica', 'password2': 'practica', 'city': 'Sevilla', 'g-recaptcha-response': 'PASSED'}# this user must not exits in db
        response = mods.get('authentication/signup', json=data, response=True) #getting the html
        self.assertEqual(response.status_code, 200)  
        response = mods.post('authentication/signup', json=data, response=True) 
        self.assertEqual(response.status_code, 200)  
        
        form = UserCreateForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid())
        user1=form.save()
        self.assertTrue(user1.id>0)#user exits
        
    #user wrong email
    def test_nuevo_usuario_fail_data(self):
        os.environ['NORECAPTCHA_TESTING'] = 'True'

        data = {'email': 'new2.mail.com', 'firs_name': 'new', 'last_name': 'new', 'birthday':'01/01/2000', 'password1': 'practica', 'password2': 'practica', 'city': 'Sevilla', 'g-recaptcha-response': 'PASSED'}
        response = mods.get('authentication/signup', json=data, response=True) #getting the html
        self.assertEqual(response.status_code, 200)   #get html    
        response = mods.post('authentication/signup', json=data, response=True) 
        self.assertEqual(response.status_code, 200) 

        form = UserCreateForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid()==False)
        #print(form)

    #user already exits 
    def test_nuevo_usuario_exits(self):
        data = {'email': 'voter1@gmail.com', 'firs_name': 'new', 'last_name': 'new', 'birthday':'01/01/2000', 'password1': 'practica', 'password2': 'practica', 'city': 'Sevilla'}# this user is saved previously
        response = self.client.post('/authentication/login/', data, format='json') 
        self.assertTrue(response.status_code, 200) #exits
        response = mods.get('authentication/signup', json=data, response=True) #getting the html
        self.assertEqual(response.status_code, 200)   #get html    
        response = mods.post('authentication/signup', json=data, response=True) 
        self.assertEqual(response.status_code, 200) 

        form = UserCreateForm(data)
        self.assertTrue(form)
        self.assertTrue(form.is_valid()==False)

    


        
   
        