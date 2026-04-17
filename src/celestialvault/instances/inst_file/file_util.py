from ...tools.FileOperations import align_width


def to_string(
    indent: str, icon: str, prefix: str, name: str, suffix: str, max_name_len: int = 0
) -> str:
    """
    将节点格式化为带缩进、前缀和后缀的字符串表示。

    :param indent: 缩进字符串。
    :param icon: 节点图标字符串。
    :param prefix: 节点名称前的前缀。
    :param name: 节点名称字符串。
    :param suffix: 节点名称后的后缀。
    :param max_name_len: 最大名称长度，用于对齐。
    :return: 格式化后的节点字符串。
    """
    return f"{indent}{icon} {prefix}{align_width(name, max_name_len)}\t{suffix}"
