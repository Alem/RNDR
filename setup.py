from distutils.core import setup
import rndr

setup(
 name = "RNDR",
 version = rndr.__version__,
 author = rndr.__author__,
 author_email = "alem@cidola.com",
 description = rndr.__desc__,
 license = rndr.__licence__,
 keywords = "templates, templating, templating engine, render templates, eval",
 url = "http://packages.python.org/rndr",
 packages = ['rndr'],
 long_description = rndr.__doc__,
 classifiers = [
     "Development Status :: 3 - Alpha",
     "License :: OSI Approved :: %s" % rndr.__licence__,
 ],
)
