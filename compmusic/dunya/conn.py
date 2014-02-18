import urlparse
import urllib
import requests

import logging
logger = logging.getLogger("dunya")

HOSTNAME = "dunya.compmusic.upf.edu"
TOKEN = None

class ConnectionError(Exception):
    pass

def set_hostname(hostname):
    global HOSTNAME
    HOSTNAME = hostname

def set_token(token):
    global TOKEN
    TOKEN = token

def _get_paged_json(path, **kwargs):
    nxt = _make_url(path, **kwargs)
    logger.debug("initial paged to %s", nxt)
    ret = []
    while nxt:
        res = _dunya_url_query(nxt)
        res = res.json()
        ret.extend(res.get("results", []))
        nxt = res.get("next")
    return ret

def _dunya_url_query(url):
    logger.debug("query to '%s'"%url)
    if not TOKEN:
        raise ConnectionError("You need to authenticate with `set_token`")
    headers = {"Authorization": "Token %s" % TOKEN}
    g = requests.get(url, headers=headers)
    if g.status_code == 404:
        # 404, we return None, otherwise we raise for other errors
        return None
    g.raise_for_status()
    return g

def _make_url(path, **kwargs):
    if not kwargs:
        kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, unicode):
            kwargs[key] = value.encode('utf8')
    url = urlparse.urlunparse((
        'http',
        HOSTNAME,
        '%s' % path,
        '',
        urllib.urlencode(kwargs),
        ''
    ))
    return url

def _dunya_query_json(path, **kwargs):
    """Make a query to dunya and expect the results to be JSON"""
    g = _dunya_url_query(_make_url(path, **kwargs))
    return g.json() if g else None

def _dunya_query_file(path, **kwargs):
    """Make a query to dunya and return the raw result"""
    g = _dunya_url_query(_make_url(path, **kwargs))
    return g.content if g else None