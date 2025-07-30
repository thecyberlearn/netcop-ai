from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.wallet_balance, 0)
        self.assertTrue(self.user.is_active)
    
    def test_wallet_balance_operations(self):
        self.assertTrue(self.user.has_sufficient_balance(0))
        self.assertFalse(self.user.has_sufficient_balance(10))
        
        self.user.add_balance(50)
        self.assertEqual(self.user.wallet_balance, 50)
        
        self.assertTrue(self.user.deduct_balance(20))
        self.assertEqual(self.user.wallet_balance, 30)
        
        self.assertFalse(self.user.deduct_balance(50))
        self.assertEqual(self.user.wallet_balance, 30)


class AuthenticationTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        user = User.objects.create_user(
            email='logintest@example.com',
            password='loginpass123'
        )
        
        url = reverse('login')
        data = {
            'email': 'logintest@example.com',
            'password': 'loginpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
