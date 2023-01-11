import os
import glob

from setuptools import find_packages, setup


def _get_requirements():
    requirements = []
    for filename in glob.iglob('**/requirements.txt', recursive=True):
        with open(filename) as f:
            requirements.extend(f.read().splitlines())
    return requirements


setup(
    name="jenkins-tools",
    description="Jenkins management utility",
    keywords=["jenkins"],
    author_email="slevy35@gmail.com",
    long_description="""Jenkins utils to help you to manage your jenkins cluster.""",
    url="https://github.com/Slevy35/jenkins-tools",
    install_requires=_get_requirements(),
    packages=find_packages(),
    version='0.1.0',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'node-manager = node_manager.main:main',
            'job-manager = job_manager.main:main',
        ],
    },
)
