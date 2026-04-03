# instances/inst_fetch.py

## 源文件
- `src/celestialvault/instances/inst_fetch.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from html import unescape`
- `from typing import Any`
- `from urllib.parse import unquote`
- `import time, random`
- `import requests`
- `import httpx`
- `from httpx import ConnectError, ConnectTimeout, PoolTimeout, ProtocolError, ReadError, ReadTimeout, ProxyError, RequestError`

## 模块常量
- 无

## 顶层函数
- 无

## 类
### `Fetcher`
- 继承: `object`
- 说明: HTTP 请求封装器，支持自动重试、代理切换和文本/二进制内容获取。
- 方法:
  - `def __init__(self, headers: dict = None, sleep_time: int = 0, wait_time: int = 5, max_repeat: int = 3, text_encoding: str = 'utf-8', verify: bool = True, clash_api: str = 'http://127.0.0.1:9097', clash_proxy_port: int = 7899, use_proxy: bool = False)`
  - `def _load_proxy_list(self)`
  - `def _switch_proxy(self, tried_proxies = None)`
  - `def init_client(self)`
  - `def obtainText(self, func: object, *args, **kwargs) -> tuple[int, Any, str]`
  - `def obtainContent(self, func: object, *args, **kwargs) -> tuple[int, Any, str]`
  - `def getText(self, url: str, *args, **kwargs) -> str`
  - `def getContent(self, url: str, *args, **kwargs) -> bytes`
  - `def postText(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> str`
  - `def postContent(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> bytes`
  - `def _auto_request(self, method, request_mode, *method_args, **method_kwargs)`
