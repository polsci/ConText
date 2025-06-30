from setuptools import setup, find_packages

with open("contextapp/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="contextapp",
    version=__version__,
    description="A browser-based concordancer and language analysis application. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Geoff Ford",
    author_email="geoffrey.ford@canterbury.ac.nz",
    url="https://github.com/polsci/ConText",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "conc",
        "Flask",
        "Flask-WTF",
        "nh3",
        "flaskwebgui",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "ConText = contextapp.context:main"
        ]
    },
    classifiers=[
    ],
)

