from django.test import TestCase
from bs4 import BeautifulSoup
from .models import CafeList

# Create your tests here.
def test_search(self):
    post_about_python = CafeList.objects.create(
        name = '파이썬',
        address = 'python',
        location_x = 130.0,
        location_y = 140.0,
        cafe_stars = 4.0
    )

    response = self.client.get('/review_list/파이썬')
    self.assertEqual(response.status_code, 200)
    soup = BeautifulSoup(response.content, 'html.parser')

    main_area = soup.find('div', id='main-area')

    self.assertIn('Search: 파이썬 (2)', main_area.text)
    self.assertNotIn(self.post_001.title, main_area.text)
    self.assertNotIn(self.post_002.title, main_area.text)
    self.assertIn(self.post_003.title, main_area.text)
    self.assertIn(post_about_python.title, main_area.text)
