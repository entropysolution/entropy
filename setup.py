try:
    from setuptools import find_packages, setup, Command
except ImportError:
    from distutils.core import find_packages, setup, Command

requires = ["pymongo", "marshmallow"]

setup(name="entropy",
      version="0.1",
      packages=find_packages(),
    #   cmdclass={"test": PyTest},
      platforms=["any"],

      install_requires = ["pymongo<=2.8", "marshmallow<=2.21.0", "six"],
      zip_safe=False,
      include_package_data=True,

      author="RJ Patawaran",
      author_email="rjpatawaran@me.com",
      keywords=["mongo", "mongodb", "pymongo", "orm"],
)