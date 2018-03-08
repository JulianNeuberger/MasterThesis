import re
import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from content.models import Content, ContentType
from turns.models import Player


def crawl_images():
    url = 'https://www.google.de/search'
    image_url_regex = re.compile(r'')

    def extract_image_src(url):
        return url

    for player in Player.objects.all():
        response = requests.get(url=url, params={
            'q': player.name,
            'tbm': 'isch',
            'tbs': 'sur:fmc'
        })

        response = BeautifulSoup(response.text, 'lxml')
        images_table = response.select('table.images_table')[0]
        assert images_table is not None
        full_size_urls = [extract_image_src(link['src']) for link in images_table.find('a')]
        for image_url in full_size_urls:
            Content.objects.create(url=image_url, type=ContentType.PICTURE, for_player=player)
