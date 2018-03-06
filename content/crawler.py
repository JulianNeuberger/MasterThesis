import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from content.models import Content, ContentType
from turns.models import Player

