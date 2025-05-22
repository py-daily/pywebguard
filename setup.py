from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pywebguard",
    version="0.1.0",
    author="py-daily",
    author_email="py-daily@gmail.com",
    description="A comprehensive security library for Python web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/py-daily/pywebguard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "ipaddress>=1.0.23",
    ],
    extras_require={
        # Framework integrations
        "fastapi": ["fastapi>=0.68.0", "starlette>=0.14.0"],
        "flask": ["flask>=2.0.0"],
        # Storage backends
        "redis": ["redis>=4.0.0"],
        "sqlite": ["aiosqlite>=0.17.0"],
        "tinydb": ["tinydb>=4.5.0"],
        # All storage backends
        "all-storage": ["redis>=4.0.0", "aiosqlite>=0.17.0", "tinydb>=4.5.0"],
        # All frameworks
        "all-frameworks": ["fastapi>=0.68.0", "starlette>=0.14.0", "flask>=2.0.0"],
        # Complete installation with all dependencies
        "all": [
            "fastapi>=0.68.0",
            "starlette>=0.14.0",
            "flask>=2.0.0",
            "redis>=4.0.0",
            "aiosqlite>=0.17.0",
            "tinydb>=4.5.0",
        ],
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pywebguard=pywebguard.cli:main",
        ],
    },
)
