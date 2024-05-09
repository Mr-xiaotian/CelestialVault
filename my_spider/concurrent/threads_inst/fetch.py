# _*_ coding: utf-8 _*_

"""
fetch.py by xianhu
"""

import logging

from .base import TPEnum, BaseThread
from ...utilities.util_funcs import get_dict_buildin
from ...utilities.util_config import CONFIG_TM_ERROR_MESSAGE


class FetchThread(BaseThread):
    """
    class of FetchThread, as the subclass of BaseThread
    """

    def __init__(self, name, worker, pool):
        """
        constructor, add proxies to this thread
        """
        BaseThread.__init__(self, name, worker, pool)
        self._proxies = None
        return

    def working(self):
        """
        procedure of fetching, auto running and return True
        """

        '''
        # ----*----
        if self._pool.get_proxies_flag() and (not self._proxies):
            self._proxies = self._pool.get_a_task(TPEnum.PROXIES)

        '''

        # ----1----
        url, url_type, task_serial = self._pool.get_a_task(TPEnum.URL_FETCH)
        print(task_serial)
        # ----2----
        fetch_state, content, proxies_state = self._worker.working(url, url_type)

        # ----3----
        if fetch_state > 0:
            self._pool.update_number_dict(TPEnum.URL_FETCH_SUCC, +1)
            self._pool.add_a_task(TPEnum.HTM_PARSE,
                                  (content, url_type, task_serial))
        elif fetch_state == 0:
            self._pool.add_a_task(TPEnum.URL_FETCH,
                                  (url, url_type, task_serial))
            logging.warning("%s repeat: %s, %s", content[0], content[1],
                            CONFIG_TM_ERROR_MESSAGE %
                            (priority, get_dict_buildin(keys), deep, url))
        else:
            self._pool.update_number_dict(TPEnum.URL_FETCH_FAIL, +1)
            logging.error("%s error: %s, %s", content[0], content[1],
                          CONFIG_TM_ERROR_MESSAGE % (priority, get_dict_buildin(keys), deep, url))

        # ----*----
        if self._pool.get_proxies_flag() and self._proxies and (proxies_state <= 0):
            if proxies_state == 0:
                self._pool.add_a_task(TPEnum.PROXIES, self._proxies)
            else:
                self._pool.update_number_dict(TPEnum.PROXIES_FAIL, +1)
            self._pool.finish_a_task(TPEnum.PROXIES)
            self._proxies = None

        # ----4----
        self._pool.finish_a_task(TPEnum.URL_FETCH)

        # ----5----
        return True
