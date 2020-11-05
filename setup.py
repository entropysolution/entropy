from setuptools import find_packages, setup, Command

class PublishCommand(Command):
    description = 'Publish package to the private PyPI repository.'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.spawn(['s3pypi', '--bucket', 'entropypi'])

setup(name="entropy",
    version="1.0",
    description='EntroPy common libraries',
    packages=find_packages(),
    platforms=["any"],
    url='http://entropyph.com',
    install_requires=[req.strip() for req in open('requirements.txt')],
    zip_safe=False,
    include_package_data=True,
    author="RJ Patawaran",
    author_email="rjpatawaran@me.com",
    keywords=["mongo", "mongodb", "pymongo", "orm"],
    cmdclass={
        'publish': PublishCommand,
    },
)