# test_imgcodecs.py

> 最后更新日期: 2026/06/28

## 作用

对 `celestialvault.instances.inst_imgcodecs.CODEC_REGISTRY` 中所有已注册图像编解码器进行统一遍历测试，覆盖纯文本、二进制字节、文本文件、二进制文件四种数据形态。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `CODEC_REGISTRY` | `src/celestialvault/instances/inst_imgcodecs.py` | 所有已注册编解码器的字典 |
| 各 codec 实现 | `src/celestialvault/instances/inst_imgcodecs.py` | 提供 `encode_*` / `decode_*` 方法 |

## 测试重点

### `test_codecs_text`

- 准备一段包含中文、特殊符号、控制字符的纯文本。
- 遍历 `CODEC_REGISTRY` 中每个编解码器：
  - `encode_text(sample_text)` → 图像
  - `decode_text(img)` → 文本
- 任一 codec 抛出异常即记为失败，最终断言全部成功。

### `test_codecs_bytes`

- 准备一段包含 `\x00`、`\xff` 等不可打印字节的二进制数据。
- 遍历所有 codec：
  - `encode_bytes(sample_data)` → 图像
  - `decode_bytes(img)` → bytes
- 断言无异常。

### `test_codecs_txt_file`

- 读取固定路径文本文件 `Q:\Project\test\text\text_txt.txt`。
- 对每个 codec：
  - `encode_txt_file(sample_text_path, True)` → 图像
  - 按规则 `<stem>(<mode_name>)(txt).png` 生成输出图像名
  - `decode_txt_image_file(image_path)` → 文本
- 断言无异常。

### `test_codecs_binary_file`

- 读取固定路径二进制文件 `Q:\Project\test\binary\test_pdf.pdf`。
- 对每个 codec：
  - `encode_binary_file(sample_bin_path, True)` → 图像
  - 按规则 `<stem>(<mode_name>)(<suffix>).png` 生成输出图像名
  - `decode_binary_image_file(image_path)` → bytes
- 断言无异常。

## 运行方式

```bash
uv run pytest tests/test_imgcodecs.py -s
```

> 文本文件与二进制文件测试依赖固定绝对路径 `Q:\Project\test\...` 存在；若路径不存在，相关测试将失败。
