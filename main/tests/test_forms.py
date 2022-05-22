import json

from django.test import TestCase
from django.http.cookie import SimpleCookie
from django.urls import reverse

from main.forms import AddMemoryForm
from main.const import TESTING_UID


class AddMemoryFormTestCase(TestCase):

    def test_empty_form(self):
        form = AddMemoryForm(data={
        })
        self.assertFalse(form.is_valid())

    def test_semi_empty_form(self):
        form = AddMemoryForm(data={
            'place': 'Palace',
        })
        self.assertFalse(form.is_valid())

    def test_filled_form(self):
        form = AddMemoryForm(data={
            'place': 'Palace',
            'description': 'This is palace',
        })
        self.assertTrue(form.is_valid())

    def test_form_send_not_filled(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude=12.0,
            description='This is palace',
        )), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_form_send_wrong(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude='tr',
            scale=[],
            place='Palace',
            description='This is palace',
        )), content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_form_send_correct(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude=12.0,
            scale=64,
            place='Palace',
            description='This is palace',
        )), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'id': 1})

        response = self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude=12.0,
            scale=64,
            place='Palace',
            description='This is palace',
        )), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'id': 2})


class DeleteButtonTestCase(TestCase):

    def test_send_not_filled(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.delete(reverse('home'), json.dumps(dict(
        )), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_send_wrong_filled1(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.delete(reverse('home'), json.dumps(dict(
            idx=1000,
        )), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_send_wrong_filled2(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.delete(reverse('home'), json.dumps(dict(
            idx=-11,
        )), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_send_wrong_filled3(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})
        response = self.client.delete(reverse('home'), json.dumps(dict(
            idx='ewcew',
        )), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_send_correct_filled(self):
        self.client.cookies = SimpleCookie({'uid': TESTING_UID})

        self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude=12.0,
            scale=64,
            place='Palace',
            description='This is palace',
        )), content_type='application/json')
        self.client.post(reverse('map'), json.dumps(dict(
            latitude=12.0,
            longitude=12.0,
            scale=64,
            place='Palace',
            description='This is palace',
        )), content_type='application/json')

        response = self.client.delete(reverse('home'), json.dumps(dict(
            idx=1,
        )), content_type='application/json')

        self.assertEqual(response.status_code, 200)
