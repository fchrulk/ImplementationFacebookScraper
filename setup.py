from setuptools import setup

exec(open("version.py").read())

setup(
    name='ImplementationFacebookScraper',
    version=__version__,
    description='Getting data from public Facebook Account/Page/Group and still on progress to scrape possible data! ',
    author='Fachrul Kurniansyah',
    maintainer='Fachrul Kurniansyah',
    maintainer_email='fchrulk@outlook.com',
    url='https://github.com/fchrulk/ImplementationFacebookScraper',
    packages=["ImplementationFacebookScraper"],
    install_requires=['requests','Unidecode','PyYAML','python_dateutil'],
)