# `celestialvault.instances.inst_fetch`

> 📅 最后更新日期: 2026/04/21

## 源文件 - `src/celestialvault/instances/inst_fetch.py`

## 模块说明

提供 HTTP 请求封装类 `Fetcher`，支持自动重试、Clash 代理切换和文本/二进制内容获取。基于 `httpx` 构建。

## 导入依赖

- `html.unescape` - HTML 实体解码
- `typing.Any` - 类型注解
- `urllib.parse.unquote` - URL 解码
- `time` - 睡眠/延迟
- `random` - 随机代理选择
- `requests` - Clash API 调用
- `httpx` - HTTP 客户端
- `httpx` 异常类: `ConnectError`, `ConnectTimeout`, `PoolTimeout`, `ProtocolError`, `ReadError`, `ReadTimeout`, `ProxyError`, `RequestError`

## 类

### `Fetcher`

- 继承: 无
- 说明: HTTP 请求封装器，支持自动重试、代理切换和文本/二进制内容获取。

- 构造函数: `__init__(self, headers=None, sleep_time=0, wait_time=5, max_repeat=3, text_encoding='utf-8', verify=True, clash_api='http://127.0.0.1:9097', clash_proxy_port=7899, use_proxy=False)`
  - 参数:
    - `headers` (`dict | None`): 自定义请求头。
    - `sleep_time` (`int`): 每次请求间隔的睡眠时间（秒），默认 `0`。
    - `wait_time` (`int`): 请求超时时间（秒），默认 `5`。
    - `max_repeat` (`int`): 最大重试次数，默认 `3`。
    - `text_encoding` (`str`): 文本响应的编码格式，默认 `'utf-8'`。
    - `verify` (`bool`): 是否验证 SSL 证书，默认 `True`。
    - `clash_api` (`str`): Clash API 地址，默认 `'http://127.0.0.1:9097'`。
    - `clash_proxy_port` (`int`): Clash 代理端口，默认 `7899`。
    - `use_proxy` (`bool`): 是否使用代理，默认 `False`。

- 方法:

  #### `_load_proxy_list(self)`
  - 签名: `_load_proxy_list(self) -> list[str]`
  - 说明: 从 Clash API 加载代理列表，按延迟排序并取前 40 个最快节点。
  - 返回值: 延迟最低的 40 个代理节点名称列表。

  #### `_switch_proxy(self, tried_proxies=None)`
  - 签名: `_switch_proxy(self, tried_proxies=None) -> None`
  - 说明: 随机切换到一个未尝试过的代理节点，并重新初始化 HTTP 客户端。
  - 参数:
    - `tried_proxies` (`set | None`): 已尝试过的代理名称集合。

  #### `init_client(self)`
  - 签名: `init_client(self) -> None`
  - 说明: 初始化 httpx 客户端（懒加载），如已存在则跳过。

  #### `obtainText(self, func, *args, **kwargs)`
  - 签名: `obtainText(self, func: object, *args, **kwargs) -> tuple[int, str]`
  - 说明: 执行请求函数并返回解码后的文本内容。
  - 参数:
    - `func`: 要执行的 httpx 请求函数（如 `cl.get` 或 `cl.post`）。
  - 返回值: `(状态码, 解码后的文本内容)` 元组。

  #### `obtainContent(self, func, *args, **kwargs)`
  - 签名: `obtainContent(self, func: object, *args, **kwargs) -> tuple[int, bytes]`
  - 说明: 执行请求函数并返回原始二进制内容。
  - 参数:
    - `func`: 要执行的 httpx 请求函数。
  - 返回值: `(状态码, 原始二进制内容)` 元组。

  #### `getText(self, url, *args, **kwargs)`
  - 签名: `getText(self, url: str, *args, **kwargs) -> str`
  - 说明: 发送 GET 请求并返回解码后的文本内容。
  - 参数:
    - `url` (`str`): 请求的 URL 地址。
  - 返回值: 解码后的文本内容。

  #### `getContent(self, url, *args, **kwargs)`
  - 签名: `getContent(self, url: str, *args, **kwargs) -> bytes`
  - 说明: 发送 GET 请求并返回原始二进制内容。
  - 参数:
    - `url` (`str`): 请求的 URL 地址。
  - 返回值: 原始二进制内容。

  #### `postText(self, url, data=None, json=None, *args, **kwargs)`
  - 签名: `postText(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> str`
  - 说明: 发送 POST 请求并返回解码后的文本内容。
  - 参数:
    - `url` (`str`): 请求的 URL 地址。
    - `data` (`Any`): 表单数据。
    - `json` (`Any`): JSON 数据。
  - 返回值: 解码后的文本内容。

  #### `postContent(self, url, data=None, json=None, *args, **kwargs)`
  - 签名: `postContent(self, url: str, data: Any = None, json: Any = None, *args, **kwargs) -> bytes`
  - 说明: 发送 POST 请求并返回原始二进制内容。
  - 参数:
    - `url` (`str`): 请求的 URL 地址。
    - `data` (`Any`): 表单数据。
    - `json` (`Any`): JSON 数据。
  - 返回值: 原始二进制内容。

  #### `_auto_request(self, method, request_mode, *method_args, **method_kwargs)`
  - 签名: `_auto_request(self, method, request_mode, *method_args, **method_kwargs) -> tuple[int, Any]`
  - 说明: 自动请求核心方法：支持直连或代理模式，失败时自动重试和切换代理。直连模式下直接请求；代理模式下遇到 403/429/503/502/302 状态码或网络异常时自动切换代理重试。
  - 参数:
    - `method`: 获取响应内容的方法（`obtainText` 或 `obtainContent`）。
    - `request_mode` (`str`): 请求方式，`'GET'` 或 `'POST'`。
  - 返回值: `(状态码, 响应内容)` 元组。
  - 异常: `RuntimeError` - 所有重试均失败时抛出。

- 用法示例:

```python
from celestialvault.instances.inst_fetch import Fetcher

# 直连模式
fetcher = Fetcher(wait_time=10, max_repeat=5)
text = fetcher.getText("https://example.com/api/data")
print(text)

# 代理模式
proxy_fetcher = Fetcher(use_proxy=True, clash_proxy_port=7899)
content = proxy_fetcher.getContent("https://example.com/image.png")

# POST 请求
response_text = fetcher.postText("https://example.com/api", json={"key": "value"})
```

- 关联: 被 `inst_save.Saver` 的下载方法（`download_text`, `download_content`, `download_image` 等）使用。
