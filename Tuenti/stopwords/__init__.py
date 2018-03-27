#  encoding: utf-8
"""
Manage the registry of stopwords.

The stopword for each language is kept in a TXT file in UTF-8 ecoding in the
current directory. To retrieve the stopwords, use the get_stopwords() function.
They are cached after loaded for the first time, so feel free to use it as many
times as you want.
"""

from __future__ import unicode_literals
import pkg_resources

import logging
LOGGER = logging.getLogger(__name__)

# Local variables for caching the results
_STOPWORDS_CACHE = {
    'available_langs': None,
    'langs': {}
}


def _list_available_languages():
    """Returns a list of available languages. Also cache the results so we
    don't touch the filesystem every time.
    """

    if _STOPWORDS_CACHE['available_langs'] is None:
        # We haven't computed this yet. Let's look up the available files to
        # infer which languages we have.
        available_langs = []

        filenames = pkg_resources.resource_listdir(__name__, '.')
        for filename in filenames:
            if filename.endswith('.txt'):
                available_langs.append(filename[:-4])

        _STOPWORDS_CACHE['available_langs'] = available_langs

        LOGGER.debug("Found stopwords for the following languages: %s",
                     ", ".join(available_langs))

    return _STOPWORDS_CACHE['available_langs']


def get_stopwords(language):
    """Retrieve the list of stopwords for the requested language."""
    # Basic treatment for input
    language = language.strip().lower()

    # Validate if we actually know the input
    available_langs = _list_available_languages()

    if language not in available_langs:
        LOGGER.warning("No stopwords found for requested language '%s'.",
                       language)
        return []

    if language not in _STOPWORDS_CACHE['langs']:
        # Language actually exists, but is not loaded
        filename = language + ".txt"

        LOGGER.debug('Loading stopwords for "%s" from file "%s"',
                     language, filename)

        contents = pkg_resources.resource_string(__name__, filename)

        words = contents.decode('utf-8').split('\n')
        words = (x.strip() for x in words)
        words = [x for x in words if x]

        # Save to the cache
        _STOPWORDS_CACHE['langs'][language] = words

    # Return the cached version
    return _STOPWORDS_CACHE['langs'][language]
