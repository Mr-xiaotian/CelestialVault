from setuptools import setup, find_packages


setup(
    name="CelestialVault",        # 项目名称
    version="1.0.0",                 # 项目版本
    author="Mr.Xiaotian",              # 作者信息
    author_email="mingxiaomingtian@gmail.com",  # 作者联系邮箱
    description="A Python package for managing celestial data.",  # 短描述
    long_description=open("README.md", encoding="utf-8").read(), # 长描述，一般从README获取
    long_description_content_type="text/markdown",       # 描述的文本格式
    url="https://github.com/Mr-xiaotian/CelestialVault", # 项目主页
    
    packages=find_packages(where="src"),    # <<< 1. 修改这里：告诉 setuptools 去 src 下找
    package_dir={"": "src"},                # <<< 2. 加上这行：映射顶级目录到 src

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10', # Python版本要求
    install_requires=[       # 依赖列表（从requirements.txt中获取或手动填写） pipreqs . --force
        "aiohttp==3.9.5",
        "beautifulsoup4==4.12.3",
        "charset_normalizer==3.3.2",
        "fitz==0.0.1.dev2",
        "httpx==0.28.1",
        "jieba==0.42.1",
        "loguru==0.7.2",
        "matplotlib==3.10.0",
        "moviepy==1.0.3",
        "mpmath==1.3.0",
        "numpy==2.2.0",
        "opencv_python==4.10.0.84",
        "pandas==2.2.3",
        "Pillow==11.0.0",
        "pillow_heif==0.16.0",
        "py7zr==0.21.0",
        "PyPDF2==3.0.1",
        "pytest==8.2.0",
        "rarfile==4.2",
        "scipy==1.14.1",
        "setuptools==69.1.1",
        "skimage==0.0",
        "tqdm==4.66.4"
    ],
    entry_points={
        'console_scripts': [
            # 如需提供命令行工具
        ],
    },
    include_package_data=False,        # 如果需要包含额外的文件(如数据文件)
    # package_data={'your_project': ['data/*.txt']}  # 指定数据文件
)