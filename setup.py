from setuptools import setup,find_packages

setup(
    name="cg-manage-rds",
    version="0.1.0",
    packages=find_packages("."),
    include_package_data=True,
    package_data={
        "cg_manage_rds": [
            "cf-app/manifest.yml",
            "cf-app/app.py"
        ]
    },
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "cg-manage-rds = cg_manage_rds.cli:main",
        ],
    },
)
