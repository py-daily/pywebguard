from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


fastapi = ["fastapi>=0.115.12", "starlette>=0.14.0", "uvicorn>=0.34.2"]
flask = ["flask>=3.1.1"]
# Storage backends
redis = ["redis>=6.1.0", "aioredis>=2.0.1"]
sqlite = ["aiosqlite>=0.21.0"]
tinydb = ["tinydb>=4.8.2"]
mongodb = ["pymongo>=4.13.0"]
postgresql = ["asyncpg>=0.30.0", "psycopg2-binary>=2.9.10"]
elasticsearch = ["elasticsearch>=9.0.1"]

all_frameworks = fastapi + flask
all_storage = redis + sqlite + tinydb + mongodb + postgresql + elasticsearch

setup(
    name="pywebguard",
    version="0.1.0",
    author="py-daily",
    author_email="pydaily32@gmail.com",
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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "ipaddress>=1.0.23",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        # Framework integrations
        "fastapi": fastapi,
        "flask": flask,
        # Storage backends
        "redis": redis,
        "sqlite": sqlite,
        "tinydb": tinydb,
        "mongodb": mongodb,
        "postgresql": postgresql,
        "elasticsearch": elasticsearch,
        # All storage backends
        "all-storage": all_storage,
        # All frameworks
        "all-frameworks": all_frameworks,
        # Complete installation with all dependencies
        "all": all_frameworks + all_storage,
        # Development dependencies
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=6.1.1",
            "pytest-asyncio>=0.26.0",
            "black>=25.1.0",
            "isort>=6.0.1",
            "mypy>=1.15.0",
            "flake8>=7.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pywebguard=pywebguard.cli:main",
        ],
    },
)
