from django.test import TestCase

from questionmark import api


class TestQuestionApi(TestCase):

    def test_asserts(self):
        api.search_product('pindakaas')
