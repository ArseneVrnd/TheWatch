from setuptools import setup, find_packages

setup(
    name="thewatch",
    packages=find_packages(),
    version="0.1.0",
    description="Grailed sales monitoring tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'aiohttp>=3.9.1',
        'beautifulsoup4>=4.12.0',
        'rich>=13.7.0',
        'python-dateutil>=2.8.2',
        'pandas>=2.1.3',
        'openpyxl>=3.1.2',
        'pydantic>=2.5.2',
        'pydantic-settings>=2.0.0',  # Added this line
        'lxml>=4.9.3',
        'aiohttp-socks>=0.8.4',
        'python-dotenv>=1.0.0'
        'fastapi>=0.95.0',
        'uvicorn>=0.21.0',
        'beautifulsoup4>=4.11.2',
        'aiohttp>=3.8.4'
]
    ],
    entry_points={
        'console_scripts': [
            'thewatch=TheWatch.monitor:main',
        ],
    },
)