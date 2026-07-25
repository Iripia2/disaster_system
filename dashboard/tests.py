from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class DashboardRoleTests(TestCase):
    def setUp(self):
        self.reporter = CustomUser.objects.create_user(
            username='reporter1',
            password='password123',
            role='reporter',
            first_name='Jane',
            last_name='Doe',
        )
        self.responder = CustomUser.objects.create_user(
            username='responder1',
            password='password123',
            role='responder',
            first_name='John',
            last_name='Smith',
        )
        self.admin = CustomUser.objects.create_user(
            username='admin1',
            password='password123',
            role='admin',
            first_name='Admin',
            last_name='User',
        )

    def test_reporter_dashboard_renders(self):
        self.client.force_login(self.reporter)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/reporter_dashboard.html')

    def test_responder_dashboard_renders(self):
        self.client.force_login(self.responder)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/responder_dashboard.html')

    def test_admin_dashboard_renders(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/admin_dashboard.html')
