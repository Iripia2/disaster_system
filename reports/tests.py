from django.test import TestCase
from django.urls import reverse

from reports.models import DisasterCategory, DisasterReport


class AnonymousReportTests(TestCase):
    def setUp(self):
        self.category = DisasterCategory.objects.create(name='Flood', icon='bi-water', is_active=True)

    def test_anonymous_report_can_be_submitted(self):
        response = self.client.post(reverse('reports:anonymous_submit'), {
            'reporter_name': 'Anonymous Caller',
            'phone_number': '07000000000',
            'category': self.category.id,
            'title': 'Bridge flooding near market',
            'description': 'Water has cut off the main route.',
            'severity': 'high',
            'address': 'Mariam Market Road',
            'city': 'Calabar',
            'lga': 'Calabar Municipality',
            'affected_count': 40,
            'incident_date': '2026-08-04T14:30',
        })

        self.assertEqual(response.status_code, 302)
        report = DisasterReport.objects.get(title='Bridge flooding near market')
        self.assertTrue(report.is_anonymous)
        self.assertIsNone(report.reporter)
        self.assertEqual(report.location.city, 'Calabar')
