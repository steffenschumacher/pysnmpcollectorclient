from requests import get, post, put, delete, Response
from time import time
from json import loads


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
        return loads(r.text)  # use stock json.loads, as older requests impl has issues with parsing
                              # MeasurementGroups (
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


class Cookie(object):
    prefix = 'snmpcollector-sess-'

    def __init__(self, key, value, expiry=None):
        self.key = key
        self.value = value
        self.expiry = expiry or time()+3600

    @classmethod
    def harvest(cls, r: Response):
        cookie = r.cookies.get(f"{cls.prefix}my_instance_cookie")
        if cookie:
            return cls(f"{cls.prefix}my_instance_cookie", cookie)
        else:
            for name, cookie in r.cookies.items():
                if name.startswith(cls.prefix):
                    return cls(name, cookie)
            else:
                raise Exception(f"No cookie in response headers: {list(r.cookies.keys())}")

    @property
    def expired(self):
        return self.expiry < time()

    @property
    def data(self):
        return {self.key: self.value}


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
        if self.cookie and not self.cookie.expired:
            return

        r = post(self.base_url + '/login', data={'username': self.user, 'password': self.pw})
        if r.status_code != 200:
            raise Exception('Unable to login: {}'.format(r.text))
        self.cookie = Cookie.harvest(r)

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
        return _raise_for(get(self._url(path), params, cookies=self.cookie.data), 'GET', path)

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
        return _raise_for(put(self._url(path), json=config, cookies=self.cookie.data), 'PUT', path)

    def create_device_config(self, config, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return:
        :rtype: dict
        """
        path = _devcfg_url(runtime=runtime)
        return _raise_for(post(self._url(path), json=config, cookies=self.cookie.data), 'POST', path)

    def delete_device_config(self, id_, runtime=False):
        """
        :param str id_:
        :param bool runtime: retrieve from runtime or db
        :return: 'deleted' if successfull
        :rtype: str
        """
        path = _devcfg_url(id_, runtime)
        return _raise_for(delete(self._url(path), cookies=self.cookie.data), 'DELETE', path)
