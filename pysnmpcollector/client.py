from requests import get, post, put, delete, Response
from time import time

cookie_key = 'snmpcollector-sess-my_instance_cookie'


def _raise_for(r, type, path):
    """
    Check response and raise if any errors - else retrieve relevant type of result (json or text)
    :param Response r:
    :param str type:
    :param str path:
    :rtype: dict|str
    """
    if r.status_code != 200:
        raise Exception('Unable to {} {}: {}'.format(type, path, r.text))
    if r.headers['Content-Type'].find('json') > 0:
        return r.json()
    else:
        return r.text


def _devcfg_url(id_=None, runtime=False):
    """
    Generate config path for a device
    :param id_:
    :param runtime:
    :return:
    """
    return '/api/cfg/snmpdevice{}{}'.format('' if not id_ else '/{}'.format(id_), '/runtime' if runtime else '')


class Client(object):

    def __init__(self, base_url, user, pw):
        """
        Constructor
        :param str base_url: eg. 'http://localhost:8090' - no trailing slash!
        :param str user:
        :param str pw:
        """
        self.base_url = base_url
        self.user = user,
        self.pw = pw
        self.cookie = None

    def _login(self):
        """
        Login routine
        :return:
        """
        if self.cookie is not None and self.cookie[1] < time():
            return

        r = post(self.base_url + '/login', data={'username': self.user, 'password': self.pw})
        if r.status_code != 200:
            raise Exception('Unable to login: {}'.format(r.text))
        if cookie_key not in r.cookies:
            raise Exception('No cookie in response headers: {}'.format(r.text))
        self.cookie = (r.cookies[cookie_key], time()+3600)

    def _url(self, path):
        """
        :param str path:
        :rtype: str
        """
        self._login()
        return self.base_url + path

    def _get(self, path, params=None):
        """
        Execute a GET request
        :param str path:
        :param dict params:
        :rtype: Response
        """
        return _raise_for(get(self._url(path), params, cookies={cookie_key: self.cookie[0]}), 'GET', path)

    def reload_config(self):
        """
        Reload all configs from database to runtime
        :return:
        """
        return self._get('/api/rt/agent/reload')

    def get_devices_info(self):
        """
        :return: all devices and their info
        :rtype: dict
        """
        return self._get('/api/rt/device/info')

    def get_devices_config(self):
        """
        :return: all devices and their config
        :rtype: dict
        """
        return self._get(_devcfg_url())

    def get_device_config(self, id_, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return:
        :rtype: dict
        """
        return self._get(_devcfg_url(id_, runtime))

    def update_device_config(self, id_, config, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return:
        :rtype: dict
        """
        path = _devcfg_url(id_, runtime)
        return _raise_for(put(self._url(path), json=config, cookies={cookie_key: self.cookie[0]}), 'PUT', path)

    def create_device_config(self, config, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return:
        :rtype: dict
        """
        path = _devcfg_url(runtime=runtime)
        return _raise_for(post(self._url(path), json=config, cookies={cookie_key: self.cookie[0]}), 'POST', path)

    def delete_device_config(self, id_, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return: 'deleted' if successfull
        :rtype: str
        """
        path = _devcfg_url(id_, runtime)
        return _raise_for(delete(self._url(path), cookies={cookie_key: self.cookie[0]}), 'DELETE', path)
