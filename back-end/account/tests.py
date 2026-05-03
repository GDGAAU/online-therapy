from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from account.models import CustomUser
from unittest.mock import patch

class AccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_email = "testuser@example.com"
        self.user_password = "TestPassword123"

        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password=self.user_password
        )

    def test_login(self):
        url = reverse('login')  
        response = self.client.post(url, {'email': self.user_email, 'password': self.user_password})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_rate_limit(self):
        url = '/api/v1/auth/jwt/create/'
        payload = {'email': self.user_email, 'password': self.user_password}
        for _ in range(5):
            response = self.client.post(url, payload)
            self.assertEqual(response.status_code, 200)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)

    def test_register_rate_limit(self):
        url = '/api/v1/auth/users/'
        payload = {'email': 'another@example.com', 'password': 'AnotherPassword123'}
        for _ in range(3):
            response = self.client.post(url, payload)
            self.assertIn(response.status_code, [201, 400])
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)

    def test_password_reset_rate_limit(self):
        url = '/api/v1/auth/users/reset_password/'
        payload = {'email': self.user_email}
        for _ in range(3):
            response = self.client.post(url, payload)
            self.assertIn(response.status_code, [200, 400])
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response.headers)

    def test_deactivate_user_blacklists_outstanding_tokens(self):
        create_url = reverse('jwt-create')
        response = self.client.post(create_url, {'email': self.user_email, 'password': self.user_password})
        self.assertEqual(response.status_code, 200)
        access_token = response.data.get('access')
        self.assertIsNotNone(access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, 200)

        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        self.assertTrue(OutstandingToken.objects.filter(user=self.user).exists())
        self.assertTrue(BlacklistedToken.objects.filter(token__user=self.user).exists())

        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, 401)

        self.user.is_active = True
        self.user.save(update_fields=['is_active'])

        response = self.client.post(create_url, {'email': self.user_email, 'password': self.user_password})
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        url = reverse('forgot-password')  
        response = self.client.post(url, {'email': self.user_email})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        print("Forgot password email link (test):", response.data.get('message'))

    def test_reset_password(self):
        uid = self.user.id
        token = "fake-reset-token"
        url = reverse('reset-password', args=[uid, token])
        new_password = "NewPass1234"
        response = self.client.post(url, {'password': new_password})
        self.assertIn(response.status_code, [200, 400])  

    def test_email_verification(self):
        uid = self.user.id
        token = "fake-token"
        url = reverse('verify-email', args=[uid, token])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 400])
        print("Verification email link (test): Click this link to verify your email:", url)  

        

    # ---------------- Google login test ----------------

    @patch('account.views.id_token.verify_oauth2_token')
    def test_google_login(self, mock_verify):
        
        #Test Google login with a mocked ID token verification
        
        mock_verify.return_value = {'email': 'googleuser@example.com'}

        url = reverse('google-login')
        response = self.client.post(url, {'token': 'fake-google-token'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged in as googleuser@example.com', response.data['message'])
        
        
        user_exists = CustomUser.objects.filter(email='googleuser@example.com').exists()
        self.assertTrue(user_exists)
