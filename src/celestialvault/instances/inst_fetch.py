from html import unescape
from typing import Any, Tuple
from urllib.parse import unquote

import time, random
import requests
import httpx

from httpx import (
    ConnectError,
    ConnectTimeout,
    PoolTimeout,
    ProtocolError,
    ReadError,
    ReadTimeout,
    ProxyError,
    RequestError,
)


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
        self.proxies = (
            {
                "http://": f"http://127.0.0.1:{clash_proxy_port}",
                "https://": f"http://127.0.0.1:{clash_proxy_port}",
            }
            if use_proxy
            else None
        )  # 🟢 不使用代理则为 None

        self.show_info = False

        self.headers = headers
        self.cl = None
        if self.use_proxy:
            self.proxy_list = self._load_proxy_list()
            self.proxy_index = 0

    def _load_proxy_list(self):
        resp = requests.get(f"{self.clash_api}/proxies")
        proxies_info = resp.json().get("proxies", {})
        global_proxy_names = proxies_info.get("GLOBAL", {}).get("all", [])
        exclude = {
            "DIRECT",
            "REJECT",
            "GLOBAL",
            "Proxy",
            "节点选择",
            "自动选择",
        }  # 需要排除的一些特殊节点

        # 收集每个代理的延迟（如果有的话）
        proxy_delays = []
        for name in global_proxy_names:
            if name in exclude:
                continue
            proxy_info = proxies_info.get(name, {})
            delay = 99999  # 默认延迟大值
            try:
                delay = proxy_info["extra"]["http://www.gstatic.com/generate_204"][
                    "history"
                ][0]["delay"]
            except (KeyError, IndexError, TypeError):
                pass  # 该节点没有延迟信息，默认99999
            proxy_delays.append((name, delay))

        # 按延迟排序，取最小的40个
        sorted_proxies = sorted(proxy_delays, key=lambda x: x[1])
        top_40 = [name for name, delay in sorted_proxies[:40]]

        # print("🌟 选出延迟最低的 40 个代理:", top_40)
        return top_40

    def _switch_proxy(self, tried_proxies=None):
        if not self.use_proxy:
            return

        if tried_proxies is None:
            tried_proxies = set()

        available_proxies = [p for p in self.proxy_list if p not in tried_proxies]
        if not available_proxies:
            # 所有代理都试过了，重新随机
            available_proxies = self.proxy_list

        next_proxy = random.choice(available_proxies)
        self.proxy_index = self.proxy_list.index(next_proxy)
        print(f"⚡️ 随机切换到节点: {next_proxy}") if self.show_info else None
        resp = requests.put(
            f"{self.clash_api}/proxies/GLOBAL", json={"name": next_proxy}
        )
        if resp.status_code == 204:
            print("✅ 切换成功!") if self.show_info else None
        else:
            (
                print("❌ 切换失败:", resp.status_code, resp.text)
                if self.show_info
                else None
            )
        time.sleep(1)
        self.cl = None
        self.init_client()

    def init_client(self):
        if self.cl is None:
            self.cl = httpx.Client(
                headers=self.headers,
                timeout=self._wait_time,
                verify=self.verify,
                proxies=self.proxies,  # 🟢 如果不使用代理，proxies=None
            )

    def obtainText(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response: httpx.Response = func(*args, **kwargs)
        response_text = response.content.decode(self._text_encoding, "ignore")
        response_text = unquote(unescape(response_text))
        return response.status_code, response_text

    def obtainContent(self, func: object, *args, **kwargs) -> Tuple[int, Any, str]:
        response: httpx.Response = func(*args, **kwargs)
        return response.status_code, response.content

    def getText(self, url: str, *args, **kwargs) -> str:
        return self._auto_request(self.obtainText, "GET", url, *args, **kwargs)[1]

    def getContent(self, url: str, *args, **kwargs) -> bytes:
        return self._auto_request(self.obtainContent, "GET", url, *args, **kwargs)[1]

    def postText(
        self, url: str, data: Any = None, json: Any = None, *args, **kwargs
    ) -> str:
        return self._auto_request(
            self.obtainText, "POST", url, data=data, json=json, *args, **kwargs
        )[1]

    def postContent(
        self, url: str, data: Any = None, json: Any = None, *args, **kwargs
    ) -> bytes:
        return self._auto_request(
            self.obtainContent, "POST", url, data=data, json=json, *args, **kwargs
        )[1]

    def _auto_request(self, method, request_mode, *method_args, **method_kwargs):
        if not self.use_proxy:
            self.init_client()
            if request_mode == "POST":
                status, content = method(self.cl.post, *method_args, **method_kwargs)
            else:
                status, content = method(self.cl.get, *method_args, **method_kwargs)
            print(f"✅ 直连成功, 状态码: {status}") if self.show_info else None
            return status, content

        tried_proxies = set()
        for _ in range(self._max_repeat):
            try:
                self.init_client()
                if request_mode == "POST":
                    status, content = method(
                        self.cl.post, *method_args, **method_kwargs
                    )
                else:
                    status, content = method(self.cl.get, *method_args, **method_kwargs)

                if status in [403, 429, 503, 502, 302]:
                    print(f"⚠️ 状态码 {status}, 需要换代理…") if self.show_info else None
                    tried_proxies.add(self.proxy_list[self.proxy_index])
                    self._switch_proxy(tried_proxies)
                    continue
                print(f"✅ 成功请求, 状态码: {status}") if self.show_info else None
                return status, content
            
            except (ConnectError, ProxyError, ConnectTimeout, ProtocolError, RequestError) as e:
                # 这些通常说明代理节点或网络本身问题 → 换代理
                print(f"⚠️ 网络级错误: {type(e).__name__}，切换代理…") if self.show_info else None
                tried_proxies.add(self.proxy_list[self.proxy_index])
                self._switch_proxy(tried_proxies)
                continue

            except (ReadTimeout, ReadError) as e:
                # 这些通常是服务器响应慢，可以原地重试一次
                print(f"⏳ 响应超时: {type(e).__name__}，重试…") if self.show_info else None
                time.sleep(random.uniform(1, 3))
                continue

            except PoolTimeout as e:
                # 连接池耗尽，多为瞬时高并发问题
                print(f"⚠️ 连接池耗尽: {type(e).__name__}，等待后重试…") if self.show_info else None
                time.sleep(random.uniform(2, 4))
                continue

        raise RuntimeError("🚫 所有节点均请求失败！")
