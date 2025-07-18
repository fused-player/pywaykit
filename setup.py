import subprocess
from setuptools import setup,find_packages
from setuptools.command.install import install


class bash_start(install):
    def run(self):
        install.run(self)

    



setup(
    name='pywaykit',
    version='0.2',
    description='Whatsapp Automation package',
    author='fused-player',
    author_email='jillelamudichakrapani@gmail.com',
    packages=find_packages(),
    install_requires=[
        'bs4',
        'screeninfo',
        'playwright',
    ],
)
