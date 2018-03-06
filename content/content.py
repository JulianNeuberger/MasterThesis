import logging
from random import randint
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from content.models import Content, ContentType
from turns.models import Player

logger = logging.getLogger('content')


class ContentInterface:
    def content_for_player_name(self, player_name, content_type) -> Optional[Content]:
        """
        Gets content from the database and returns it, corresponding to the given player and content type

        :param player_name: a player object from turns
        :param content_type: optional, type of content to retrieve
        :return: a Content object, or None, if no object was found with given player name and content type
        """
        raise NotImplementedError()


class SimpleContentInterface(ContentInterface):
    def content_for_player_name(self, player_name, content_type=None) -> Optional[Content]:
        if content_type is not None:
            content_type = ContentType.for_name(content_type)
        try:
            player = Player.objects.get(name=player_name)
        except ObjectDoesNotExist:
            # TODO: what to do, when we get a non existent player name? is this even possible?
            # TODO: in that case --> check Dialogflow entities
            logger.warning(
                'Tried to retrieve content for non existent player "{}", '
                'check Dialogflow entities and add player to database, if he exists there'.format(player_name)
            )
            return None

        kwargs = {'for_player': player}
        if content_type is not None and content_type is not ContentType.ANYTHING:
            kwargs['type'] = content_type
        contents = Content.objects.filter(**kwargs).all()
        num_contents = len(contents)

        if num_contents == 0:
            return None
        return contents[randint(0, len(contents) - 1)]
