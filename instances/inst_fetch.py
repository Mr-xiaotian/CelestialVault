import httpx
from typing import Tuple, Any
from html import unescape
from urllib.parse import unquote
from aiohttp import ClientSession
from aiohttp.client import ClientTimeout


class Fetcher(object):
    """
    class of Fetcher, must include function working()
    """

    def __init__(self, headers=None, sleep_time=0, wait_time=5, 
                 max_repeat=3, text_encoding = 'utf-8'):
        """
        constructor
        :param sleep_time: default 0, sleeping time before fetching
        :param max_repeat: default 3, maximum repeat count of fetching
        """
        self._sleep_time = sleep_time
        self._wait_time = wait_time
        self._max_repeat = max_repeat
        self._text_encoding = text_encoding

        self.headers = headers
        self.cl = None  # 延迟初始化

    def init_client(self):
        if self.cl is None:
            self.cl = httpx.Client(headers=self.headers, timeout=self._wait_time)

    def obtainText(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response = func(*args, **kwargs)
        response_text = response.content.decode(self._text_encoding, 'ignore')
        # print(response_text)
        response_text = unquote(unescape(response_text))

        '''
        re_charset = re.compile('charset=(.+)', re.S)
        charset = re_charset.search(response.headers['content-type']).group(1)
        '''

        return 1, (response.status_code, response_text), ''
    
    def obtainContent(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response = func(*args, **kwargs)
        return 1, (response.status_code, response.content), ''

    def getText(self, url: str, *args, **kwargs) -> Tuple[int, Any, str]:
        self.init_client()
        return self.obtainText(self.cl.get, url=url,
                               *args, **kwargs)[1][1]

    def postText(self, url: str, *args, **kwargs) -> Tuple[int, Any, str]:
        self.init_client()
        return self.obtainText(self.cl.post, url=url, 
                               *args, **kwargs)[1][1]
    
    def getContent(self, url: str, *args, **kwargs) -> Tuple[int, Any, str]:
        self.init_client()
        return self.obtainContent(self.cl.get, url=url,
                               *args, **kwargs)[1][1]

    def postText(self, url: str, *args, **kwargs) -> Tuple[int, Any, str]:
        self.init_client()
        return self.obtainContent(self.cl.post, url=url, 
                               *args, **kwargs)[1][1]
    
    # 以下为异步代码, 需要结合my_thread中的start_async与run_in_async使用
    async def getText_async(self, url, encoding='utf-8'):
        async with self.se_async.get(url) as response:
            content = await response.text(encoding=encoding)
        return unquote(unescape(content))
    
    async def getContent_async(self, url):
        async with self.se_async.get(url) as response:
            content = await response.read()
        return content
    
    async def start_session(self):
        timeout = ClientTimeout(total=self._wait_time)
        self.se_async = ClientSession(timeout=timeout)

    async def close_session(self):
        await self.se_async.close()
