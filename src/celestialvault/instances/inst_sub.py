import regex as re
from html import unescape
from pathlib import Path
from urllib.parse import unquote

from ..tools.FileOperations import handle_folder_files
from ..tools.TextTools import pro_slash, safe_open_txt


class Suber:
    def __init__(self):
        # Characters that need both lookbehind and lookahead checks
        self.both_check_chars = "#|◆|\*|＊|=|＝|…|_|～|—|－|\n"

        # Characters that need only lookahead checks
        self.lookahead_only_chars = (
            '\]|』|」|】|》|\)|）|\}|\!|！|\?|？|\||”|"|\.|。|章|：|:'
        )

        # Characters that need only lookbehind checks
        self.lookbehind_only_chars = "章节|作者|字数|20|第|（|\(|\{|「|\[|【|<"

        self.regex_remove_unwanted_newlines = [
            # 移除不在某些标点符号后的换行符
            (
                f"(?<!{self.both_check_chars}|{self.lookahead_only_chars})(\n+)(?!{self.both_check_chars}|{self.lookbehind_only_chars})",
                "",
            ),
        ]

        self.special_character_removal = [
            (
                "(\t|\r|\f|\v|\0|　| |||\u001e|\x1e)+",
                "",
            ),  # 移除制表符、回车符、换页符、垂直制表符、空字符、全角空格和特殊符号
            ("\~", "-"),  # 将波浪号替换为连字符
            # ("(?<!章)[ \t]+", ""),  # 🟢 新增：不在章后面的空格或制表符

        ]

        self.newline_handling = [
            ("(?<!\n)\n(?!\n)", "\n\n"),  # 确保单独的换行符前后有两个换行符
            ("(\n){3,}", "\n\n"),  # 限制连续换行符的数量为最多2个
        ]

        self.html_md_handling = [
            ("<br>", "\n"),  # 替换 HTML 换行标签为换行符
            ("<p>", ""),
            ("</p>", "\n"),  # 替换 HTML 段落标签
            ("<code.{0,50}?>", "```\n"),
            ("</code>", "```"),  # 替换 <code> 标签为 Markdown 代码块标记
            ("(?<!\n\n)<code>", "\n\n<code>"),
            ("</code>(?!\n\n)", "</code>\n\n"),  # 确保 <code> 标签前后有两个换行符
            ("(?<!\n)```", "\n```"),
            ("```(?!\n)", "```\n"),  # 确保 Markdown 代码块标记前后有换行符
        ]

        self.sub_text_list = self.special_character_removal + self.regex_remove_unwanted_newlines + self.newline_handling

        self.sub_name_list = [
            ("：", "_"),
            (":", "_"),
            (r"\\", "_"),
            ("/", "_"),
            ("\|", "_"),
            ("\*", "_"),
            ("-", "_"),
            ('"', "_"),
            ("'", "_"),
            ("？", ""),
            ("\?", ""),
            (r"\t", "_"),
            ("\.+", "_"),
            ("<", "_"),
            (">", "_"),
        ]

    def clear_book_folder(
        self, folder_path: Path | str, execution_mode: str = "thread"
    ):
        rules = {".txt": (self.clear_book, lambda a: a)}

        return handle_folder_files(
            folder_path, rules, execution_mode, progress_desc="Clearing book folder"
        )

    def clear_book(self, book_path: Path, new_path: Path):
        book_text = safe_open_txt(book_path)

        if book_text is None:
            raise ValueError("无法使用检测到的编码解码文件")

        # 清理文本并写入新文件
        book_text = self.clear_text(book_text)
        new_path.write_text(book_text, encoding="utf-8")

    def clear_text(self, text):
        text = pro_slash(text)
        text = unquote(unescape(text))

        for sub in self.sub_text_list:
            text = re.sub(sub[0], sub[1], text, flags=re.S)

        return text.strip()

    def sub_name(self, name: str) -> str:
        # 替换非法字符
        for sub in self.sub_name_list + self.special_character_removal:
            name = re.sub(sub[0], sub[1], name)

        # 平台文件名最大长度限制
        # 通常 Windows 为 255，Linux/Mac 也类似；更严谨可以写个平台判断
        max_len = 50

        # 如果超过最大长度，按 2/4 和 1/4 拼接
        if len(name) > max_len:
            front_len = (max_len * 2) // 4
            back_len = max_len // 4
            name = f"{name[:front_len]}(省略){name[-back_len:]}"

        return name
