from setuptools import setup, find_packages

setup(
    name='cf-manage-rds',
    version='0.1.0',
    packages=['lib'],
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'cf-manage-rds = lib.cli:main',
        ],
    },
)