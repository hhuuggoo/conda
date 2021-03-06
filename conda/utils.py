from __future__ import print_function, division, absolute_import

import sys
import hashlib
import tempfile
import collections
from functools import partial
from os.path import abspath, isdir


def try_write(dir_path):
    assert isdir(dir_path)
    try:
        with tempfile.TemporaryFile(prefix='.conda-try-write',
                                    dir=dir_path, mode='wb') as fo:
            fo.write(b'This is a test file.\n')
        return True
    except OSError:
        return False


def hashsum_file(path, mode='md5'):
    with open(path, 'rb') as fi:
        h = hashlib.new(mode)
        while True:
            chunk = fi.read(262144)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def md5_file(path):
    return hashsum_file(path, 'md5')


def url_path(path):
    path = abspath(path)
    if sys.platform == 'win32':
        path = '/' + path.replace(':', '|')
    return 'file://%s' % path


def human_bytes(n):
    """
    Return the number of bytes n in more human readable form.
    """
    if n < 1024:
        return '%d B' % n
    k = (n - 1) / 1024 + 1
    if k < 1024:
        return '%d KB' % k
    return '%.1f MB' % (float(n) / (2**20))


class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args, **kw):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args, **kw)
        key = (args, frozenset(kw.items()))
        if key in self.cache:
            return self.cache[key]
        else:
            value = self.func(*args, **kw)
            self.cache[key] = value
            return value


# For instance methods only
class memoize(object): # 577452
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)
    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(kw.items()))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res
