from setuptools import setup, find_packages


setup(
    name="CelestialVault",  # 项目名称
    version="1.0.1",  # 项目版本
    author="Mr.Xiaotian",  # 作者信息
    author_email="mingxiaomingtian@gmail.com",  # 作者联系邮箱
    description="A Python package for managing celestial data.",  # 短描述
    long_description=open(
        "README.md", encoding="utf-8"
    ).read(),  # 长描述，一般从README获取
    long_description_content_type="text/markdown",  # 描述的文本格式
    url="https://github.com/Mr-xiaotian/CelestialVault",  # 项目主页
    packages=find_packages(where="src"),  # <<< 1. 修改这里：告诉 setuptools 去 src 下找
    package_dir={"": "src"},  # <<< 2. 加上这行：映射顶级目录到 src
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Python版本要求
    install_requires=[
        "numpy>=1.26",
        "pandas>=2.2",
        "mpmath>=1.3",
        "regex>=2023.0",
        "bidict>=0.22",
        "reedsolo>=1.7",
        "charset-normalizer>=3.3",
        "jieba>=0.42",
        "pillow>=10.0",
        "pillow-heif>=0.15",
        "rarfile>=4.1",
        "py7zr>=0.20",
        "httpx>=0.27",
        "requests>=2.32",
        "tqdm>=4.66",
        "loguru>=0.7",
        "networkx>=3.2",
        "beautifulsoup4>=4.12",
        # "scikit-image>=0.24",  # ← 暂时注释掉（Python 3.14 不兼容）
        "matplotlib>=3.9",  # 可选：用于图像显示
    ],
    entry_points={
        "console_scripts": [
            # 如需提供命令行工具
        ],
    },
    include_package_data=False,  # 如果需要包含额外的文件(如数据文件)
    # package_data={'your_project': ['data/*.txt']}  # 指定数据文件
)
