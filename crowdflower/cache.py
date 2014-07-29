import os
import re
import json
import unicodedata
from crowdflower import logger


def clean_filename(filename):
    '''
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django, partly, via http://stackoverflow.com/q/295135/424651

    Django is BSD licensed, so, it's cool.
    '''
    filename_unicode = unicode(filename)
    filename_normalized = unicodedata.normalize('NFKD', filename_unicode)
    # reduce to ascii charset
    filename_ascii = filename_normalized.encode('ascii', 'ignore')
    # delete everything that's not a word character, whitespace, _, or -
    filename_cleaned = re.sub(r'[^\w\s_-]', '', filename_ascii)
    # turn all sequences of whitespace to a single space
    filename_collapsed = re.sub(r'\s+', ' ', filename_cleaned).strip()
    # remove leading hyphens (less painful in Linux)
    filename_nice = filename_collapsed.lstrip('-')
    return filename_nice


def flatten(obj):
    if hasattr(obj, '__iter__'):
        # dicts are iterable, but we don't want to flatten them into a list
        if not isinstance(obj, dict):
            return list(obj)
    return obj


def keyfunc(instance, func_attr):
    cache_key_values = [getattr(instance, cache_key_attr) for cache_key_attr in instance._cache_key_attrs]
    return '%s[%s].%s' % (instance.__class__.__name__, ':'.join(map(str, cache_key_values)), func_attr)


def cacheable(name=None):
    '''An object method decorator. Use like:

    class User(object):
        _cache_key_attrs = ('user_id',)

        def __init__(self, user_id):
            self.user_id = user_id
            self._cache = FilesystemCache()

        @cacheable()
        def actions(self):
            yield 'logged in'
            yield 'changed password'
            yield 'searched for somethign'
            # etc.

        @cacheable('tags')
        def get_tags(self):
            return ['a', 'b']

        tags = property(get_tags)

    The class it is used in must have a `_cache_key_attrs` attribute and a `_cache` Cache instance.
    '''
    def decorator(func):
        func_attr = name or func.__name__
        def wrapper(self, *args, **kwargs):
            key = keyfunc(self, func_attr)
            value = self._cache.get(key)
            if value is None:
                logger.info('cache miss; fetching "%s" and writing to cache', key)
                # self refers to the instance, which SHOULD have a ._cache attribute
                value = func(self, *args, **kwargs)
                value = flatten(value)
                self._cache.put(key, value)
            else:
                logger.info('cache hit; reading "%s" from cache', key)
            return value
        return wrapper
    return decorator


class AbstractCache(object):
    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def remove(self, key):
        raise NotImplementedError

    def removeAll(self):
        raise NotImplementedError


class NoCache(AbstractCache):
    def get(self, key):
        return None

    def put(self, key, value):
        pass

    def remove(self, key):
        pass

    def removeAll(self):
        pass


class FilesystemCache(AbstractCache):
    def __init__(self, dirpath='/tmp/crowdflower'):
        self.dirpath = dirpath
        if not (os.path.exists(dirpath) and os.path.isdir(dirpath)):
            # this should rightly fail if dirpath is a file, or cannot be accessed
            os.makedirs(dirpath)

    def _filename(self, key):
        return os.path.join(self.dirpath, clean_filename(key)) + '.json'

    def get(self, key):
        filepath = self._filename(key)
        if os.path.exists(filepath):
            with open(filepath) as fp:
                return json.load(fp)

    def put(self, key, value):
        filepath = self._filename(key)
        with open(filepath, 'w') as fp:
            json.dump(value, fp)

    def remove(self, key):
        filepath = self._filename(key)
        if os.path.exists(filepath):
            os.remove(filepath)

    def removeAll(self):
        for filename in os.listdir(self.dirpath):
            filepath = os.path.join(self.dirpath, filename)
            os.remove(filepath)
