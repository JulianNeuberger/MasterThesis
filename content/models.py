from typing import Optional

from django.db import models
from enumfields import EnumField, Enum

from turns.models import Player


class ContentType(Enum):
    GIF = 'gif'
    PICTURE = 'pic'
    VIDEO = 'vid'
    ARTICLE = 'art'
    INTERVIEW = 'int'
    ANYTHING = 'any'

    @staticmethod
    def for_name(content_type_name: str) -> Optional['ContentType']:
        """
        Searches and returns the corresponding Enum entry for a given content-type-name

        :param content_type_name: the name of content type, case does not matter
        :return: the found content type or None, if no type was found
        """
        try:
            return ContentType[content_type_name.upper()]
        except KeyError:
            return None


class Content(models.Model):
    url = models.CharField(max_length=1024, null=False)
    type = EnumField(ContentType, max_length=3)

    for_player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return '<Content: {}({})>'.format(self.type, self.for_player.name)
