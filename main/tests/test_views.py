from django.http.cookie import SimpleCookie
from django.test import TestCase
from django.urls import reverse

from main.const import TESTING_UID
from main.models import User


class WrongCookies(TestCase):

    # Relocate cookie verification into auth system which is not enabled
    # def test_home_empty_cookie(self):
    #     response = self.client.get(reverse('home'))
    #     self.assertRedirects(response, reverse('welcome'))
    #
    # def test_home_wrong_cookie(self):
    #     self.client.cookies = SimpleCookie({'uid': '12345'})
    #     response = self.client.get(reverse('home'))
    #     self.assertEquals(response.status_code, 404)
    #
    # def test_home_wrong_cookie_format(self):
    #     self.client.cookies = SimpleCookie({'uid': 'bebebe'})
    #     response = self.client.get(reverse('map'))
    #     self.assertRedirects(response, reverse('welcome'))

    def test_home_correct_uid_user_not_exist(self):
        self.client.cookies = SimpleCookie({"uid": TESTING_UID})
        response = self.client.get(reverse("map"))
        self.assertEquals(response.status_code, 404)

    # def test_map_empty_cookie(self):
    #     response = self.client.get(reverse('map'))
    #     self.assertRedirects(response, reverse('welcome'))
    #
    # def test_map_wrong_cookie(self):
    #     self.client.cookies = SimpleCookie({'uid': '12345'})
    #     response = self.client.get(reverse('map'))
    #     self.assertEquals(response.status_code, 404)
    #
    # def test_map_correct_uid_user_not_exist(self):
    #     self.client.cookies = SimpleCookie({'uid': TESTING_UID})
    #     response = self.client.get(reverse('map'))
    #     self.assertEquals(response.status_code, 404)


class CorrectCookies(TestCase):
    def setUp(self):
        User.objects.create(
            uid=TESTING_UID,
            first_name="Александр",
            last_name="Никитин",
            avatar="",
        )

    def test_home_cookie(self):
        self.client.cookies = SimpleCookie({"uid": TESTING_UID})
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_map_cookie(self):
        self.client.cookies = SimpleCookie({"uid": TESTING_UID})
        response = self.client.get(reverse("map"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "map.html")

    def test_welcome(self):
        response = self.client.get(reverse("welcome"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")
