import logging
from re import compile

from content.models import ContentType

logger = logging.getLogger('content')


class Template:
    _regex = compile(r'{([^$}]*)\${([a-zA-Z0-9-_]*)}([^$}]*)}')

    def __init__(self, pattern):
        """
        Create a new Template.
        Takes a string, that represents the pattern, this template uses. I can contain placeholders of the from
        {<prefix>${<keyword>}<postfix>}, where pre- and postfix are arbitrary sub-strings, that may not contain
        $ and {/} for pre/postfix respectively.
        keyword is a substring marking an entry in a dictionary like object, with which it is to replaced by
        self.substitute

        Example:
        template = Template('I am{ ${name}}!')
        print(template.substitute({'name':'Will'})) # prints "I am Will!"
        print(template.substitute({}))              # prints "I am!"


        :param pattern: the template pattern string
        """
        self._pattern = pattern
        self._groups = Template._regex.findall(self._pattern)

    def substitute(self, replacements=None):
        """
        Replaces the occurrences of placeholders by their corresponding values given in key word arguments.
        If the corresponding value in kwargs is empty, it will replace the placeholder with the empty string
        and move on.

        :param replacements: dictionary of values to replace the placeholders with
        :return: the string "pattern" given in __init__ with replaced placeholders
        """
        if replacements is None:
            replacements = {}
        ret = self._pattern
        for prefix, keyword, postfix in self._groups:
            value = replacements.get(keyword, None)
            replacement = ''
            if value is not None:
                replacement = replacement.join((prefix, value, postfix))
            ret = Template._regex.sub(replacement, ret, count=1)
        return ret
