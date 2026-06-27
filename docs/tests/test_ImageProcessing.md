# test_ImageProcessing.py

> 最后更新日期: 2026/06/28

## 作用

验证 `celestialvault.tools.ImageProcessing` 中 PNG 文本块（tEXt chunk）写入与读取能力，测试图像元数据的往返一致性。

## 被测模块

| 模块 | 文件 | 说明 |
|------|------|------|
| `create_image_with_text_chunk` | `src/celestialvault/tools/ImageProcessing.py` | 在 PNG 中嵌入文本元数据 |
| `read_text_chunks` | `src/celestialvault/tools/ImageProcessing.py` | 读取 PNG 中的文本块 |

## 测试重点

### `test_create_image_with_text_chunk`

- 使用 Pillow 创建一张 `100x100` 的白色 `RGB` 图像。
- 调用 `create_image_with_text_chunk` 写入元数据：
  - `Author`: `Vault`
  - `Comment`: `Hello from CelestialVault!`
- 写入路径为固定绝对路径 `Q:\Project\test\test_meta.png`。
- 随后调用 `read_text_chunks` 读取同一路径，打印读取到的元数据字典。

## 运行方式

```bash
uv run pytest tests/test_ImageProcessing.py -s
```

> 该测试依赖本地 `Q:\Project\test` 目录存在且有写入权限。若路径不可用，测试会抛出文件系统异常。
