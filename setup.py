import os

from setuptools import setup, find_packages


this_dir = os.path.dirname(__file__)
readme_filename = os.path.join(this_dir, 'README.md')
requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_NAME = "nanga-ad-library"
PACKAGE_VERSION = "1.0.12"
PACKAGE_AUTHOR = "Nanga"
PACKAGE_AUTHOR_EMAIL = "hello@spark.do"
PACKAGE_URL = "https://github.com/Spark-Data-Team/nanga-ad-library"
PACKAGE_DOWNLOAD_URL = "https://github.com/Spark-Data-Team/nanga-ad-library/tarball/" + PACKAGE_VERSION
PACKAGES = find_packages()
INCLUDE_MANIFEST = True  # Inclure les fichiers définis dans MANIFEST.in
PACKAGE_LICENSE = "GNU General Public License v3 (GPLv3) (gpl-3.0)"
PACKAGE_DESCRIPTION = "The Nanga Ad Library developed by the ⭐️ Spark Tech team"

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    requirements_lines = f.read().splitlines()

    PACKAGE_INSTALL_REQUIRES = []
    DEPENDENCY_LINKS = []

    for line in requirements_lines:
        line = line.strip()
        if line.lower().startswith(('http://', 'https://')):
            DEPENDENCY_LINKS.append(line)
        else:
            PACKAGE_INSTALL_REQUIRES.append(line)

    print(PACKAGE_INSTALL_REQUIRES)

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    packages=PACKAGES,
    include_package_data=INCLUDE_MANIFEST,
    license=PACKAGE_LICENSE,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=PACKAGE_INSTALL_REQUIRES,
    long_description_content_type="text/markdown",
    dependency_links=DEPENDENCY_LINKS
)