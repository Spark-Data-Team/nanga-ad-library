import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from nanga_ad_library.utils import get_sdk_version

this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_NAME = "nanga-ad-library"
PACKAGE_VERSION = get_sdk_version().replace("v", "")
PACKAGE_AUTHOR = "Nanga"
PACKAGE_AUTHOR_EMAIL = "hello@spark.do"
PACKAGE_URL = "https://github.com/Spark-Data-Team/nanga-ad-library"
PACKAGE_DOWNLOAD_URL = "https://github.com/Spark-Data-Team/nanga-ad-library/tarball/" + PACKAGE_VERSION
PACKAGES = ["nanga_ad_library"]
PACKAGE_LICENSE = "LICENSE.txt"
PACKAGE_DESCRIPTION = "The Nanga Ad Library developed by the ⭐️ Spark Tech team"

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    PACKAGE_INSTALL_REQUIRES = []
    DEPENDENCY_LINKS = []

    for line in f:
        line = line.strip()
        if line.lower().startswith(('http://', 'https://')):
            DEPENDENCY_LINKS.append(line)
        else:
            PACKAGE_INSTALL_REQUIRES.append(line)

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    packages=PACKAGES,
    license=PACKAGE_LICENSE,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=PACKAGE_INSTALL_REQUIRES,
    long_description_content_type="text/markdown",
    dependency_links=DEPENDENCY_LINKS
)