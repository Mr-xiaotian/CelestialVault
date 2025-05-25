from html import unescape
from typing import Any, Tuple
from urllib.parse import unquote

import time
import requests
import httpx


class Fetcher:
    def __init__(
        self,
        headers: dict = None,
        sleep_time: int = 0,
        wait_time: int = 5,
        max_repeat: int = 3,
        text_encoding: str = "utf-8",
        verify: bool = True,
        clash_api: str = "http://127.0.0.1:9097",
        clash_proxy_port: int = 7899,
        use_proxy: bool = False,  # 🟢 新增参数：是否使用代理
    ):
        self._sleep_time = sleep_time
        self._wait_time = wait_time
        self._max_repeat = max_repeat
        self._text_encoding = text_encoding
        self.verify = verify
        self.use_proxy = use_proxy  # 🟢 保存是否使用代理的开关
        self.clash_api = clash_api
        self.proxies = {
            "http://": f"http://127.0.0.1:{clash_proxy_port}",
            "https://": f"http://127.0.0.1:{clash_proxy_port}",
        } if use_proxy else None  # 🟢 不使用代理则为 None

        self.headers = headers
        self.cl = None
        if self.use_proxy:
            self.proxy_list = self._load_proxy_list()
            self.proxy_index = 0

    def _load_proxy_list(self):
        resp = requests.get(f"{self.clash_api}/proxies")
        proxies_info = resp.json().get("proxies", {})
        proxy_names = proxies_info.get("GLOBAL", {}).get("all", [])
        exclude = ["DIRECT", "REJECT", "GLOBAL", "Proxy"]
        return [p for p in proxy_names if p not in exclude]

    def _switch_proxy(self):
        if not self.use_proxy:
            return  # 🟢 如果没启用代理，直接返回
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
        next_proxy = self.proxy_list[self.proxy_index]
        print(f"⚡️ 切换到节点: {next_proxy}")
        resp = requests.put(f"{self.clash_api}/proxies/GLOBAL", json={"name": next_proxy})
        if resp.status_code == 204:
            print("✅ 切换成功!")
        else:
            print("❌ 切换失败:", resp.status_code)
        time.sleep(1)

    def init_client(self):
        if self.cl is None:
            self.cl = httpx.Client(
                headers=self.headers,
                timeout=self._wait_time,
                verify=self.verify,
                proxies=self.proxies  # 🟢 如果不使用代理，proxies=None
            )

    def obtainText(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response = func(*args, **kwargs)
        response_text = response.content.decode(self._text_encoding, "ignore")
        response_text = unquote(unescape(response_text))
        return response.status_code, response_text

    def obtainContent(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response = func(*args, **kwargs)
        return response.status_code, response.content

    def getText(self, url: str, *args, **kwargs) -> str:
        return self._auto_request(self.obtainText, "GET", url, *args, **kwargs)[1]

    def getContent(self, url: str, *args, **kwargs) -> bytes:
        return self._auto_request(self.obtainContent, "GET", url, *args, **kwargs)[1]
    
    def postText(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> str:
        return self._auto_request(self.obtainText, "POST", url, data=data, json=json, *args, **kwargs)[1]

    def postContent(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> bytes:
        return self._auto_request(self.obtainContent, "POST", url, data=data, json=json, *args, **kwargs)[1]

    def _auto_request(self, method, request_mode, *method_args, **method_kwargs):
        if not self.use_proxy:
            self.init_client()
            if request_mode == "POST":
                status, content = method(self.cl.post, *method_args, **method_kwargs)
            else:
                status, content = method(self.cl.get, *method_args, **method_kwargs)
            print(f"✅ 直连成功, 状态码: {status}")
            return status, content

        for attempt in range(self._max_repeat):
            try:
                self.init_client()
                if request_mode == "POST":
                    status, content = method(self.cl.post, *method_args, **method_kwargs)
                else:
                    status, content = method(self.cl.get, *method_args, **method_kwargs)
                if status in [403, 429, 503, 502, 302]:
                    print(f"⚠️ 状态码 {status}, 需要换代理…")
                    self._switch_proxy()
                    continue
                print(f"✅ 成功请求, 状态码: {status}")
                return status, content
            except (httpx.RequestError, httpx.ProxyError) as e:
                print(f"❌ 代理请求异常: {e}, 切换代理…")
                self._switch_proxy()
        raise RuntimeError("🚫 所有节点均请求失败！")

