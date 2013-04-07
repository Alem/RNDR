__prog__    = "RNDR"
__author__  = "Z. Alem"
__licence__ = "MIT License"
__version__ = "1.0.1"
__home__    = "http://rndrengine.com"
__repo__    = "http://github.com/Alem/RNDR"
__pypi__    = "https://pypi.python.org/pypi/RNDR"
__tag__     = "A simple and powerful templating engine."
__desc__    = """
RNDR is a simple templating engine that unleashes the
full power of Python within templates.

Deriving much inspiration from PHP's templating system, RNDR
aims to exploit Python's inherent utility for templating in
a manner that is simple, configurable, and requiring little to learn.
"""
__usage__ = """
Usage
-----

Syntax
~~~~~~
RNDR's syntax is easy to learn as it involves little more than
enclosing a single-line Python statement within a pair of tags. 

These tags, the start-tag and the end-tag, are by default ``@R`` and ``R@``
respectively. 

>>> r = RNDR( 
... "<xml>"
... "@R echo( 1 + 1 ) R@"
... "</xml>" 
... )
>>> r.render()
'<xml>2</xml>'

The output function ``echo`` is used in-place of Python's ``print`` as the latter
appends a new line, which may or may not be desirable.

Rather than calling the ``echo`` function one may also use the output tag:
a start tag appended, by default, with an equal sign:

>>> r = RNDR( 
... "<xml>"
... "@R= 1 + 1  R@"
... "</xml>" 
... )
>>> r.render()
'<xml>2</xml>'

The Python language groups the statement blocks of control structures through
the use of indentation. Unfortunately, using indentation as a means for
managing control-structures within templates is restrictive, fragile, and
generally unpleasant.

In its place RNDR allows control structures to be explicitly terminated by
providing a control-structure termination statement: ``end<control-structure>``.

>>> r = RNDR( 
... "<html>"
... " Hello"
... "@R if 1+1 is 2: R@"
... " World! "
... "@R endif R@"
... "</html>" 
... )
>>> print( r.render() )
<html> Hello World! </html>

The syntax described so far is akin to (and drew its inspiration from) the PHP
templating engine.

Much like the PHP templating engine, there is no esoteric or neutered
templating language to learn: RNDR simply executes Python code placed within
statement tags. 

>>> r = RNDR(
... "<html>"
... "@R for i in [1,2,3]: R@"
... "@R= i R@ "
... "@R endfor R@"
... "</html>"
... )
>>> print( r.render() )
<html>1 2 3 </html>

>>> r = RNDR(
... "<html>"
... "@R i = 0 R@"
... "@R while True: R@"
...     "@R i += 1 R@"
...     "@R if i == 3: R@"
...       " I'm finally three! "
...     "@R break R@"
...     "@R endif R@"
... "@R endwhile R@"
... "</html>"
... )
>>> print( r.render() )
<html> I'm finally three! </html>

One can take this to great extremes:

>>> r = RNDR(
... "<html>"
... "@R try: R@"
...     "@R 1/0 R@"
... "@R except Exception as e: R@"
...     " @R= e R@ is fun! "
... "@R endtry R@"
... "</html>"
... )
>>> print( r.render() )
<html> integer division or modulo by zero is fun! </html>

With respect to the principle of concern separation, seldom could
such practice be considered a good idea. 
Ideally, complex or sensitive functionality should be contained in a domain
removed from presentation; logic delegated to the template should be the
simplest kind able to perform the given task.

Templates and Context
~~~~~~~~~~~~~~~~~~~~~
RNDR accepts templates in the form of Python strings ( both bytestrings and
unicode ), and file objects.

>>> f = open('test.xml','w')
>>> r = f.write( 
... "<xml>"
... "@R= 1+1 R@"
... "</xml>" 
... )
>>> f.close()
>>> r = RNDR( open('test.xml') )
>>> r.render()
'<xml>2</xml>'

RNDR also accepts context variables: the variables that will provide the
namespace for statements found in the template.

>>> r = RNDR( 
... "<xml>"
... "@R= my_var R@"
... "</xml>" 
... )
>>> r.render( {'my_var': 'Hello'} )
'<xml>Hello</xml>'

These context variables may be of any type.

>>> r = RNDR( 
... "<xml>"
... "@R= my_func('Moe') R@"
... "</xml>" 
... )
>>> r.render( {'my_func': lambda x: "Hello " + x } )
'<xml>Hello Moe</xml>'
"""
__config__="""
Configuration
-------------

RNDR permits the configuration of a few of its features: tags, 
control structure tracking, and the output function used to print
rendered components.

Tags
~~~~
Start tags, end tags, and output suffix tags are all customizable.

>>> identical_tags_config = Config( 
...   start_tag = '||', end_tag='||' 
... )
>>> r = RNDR( 
... "<html>"
... " Hello"
... "|| if 1+1 is 3: ||"
... " Fail"
... "|| else: ||"
... " World! "
... "|| endif ||"
... "</html>", identical_tags_config
... )
>>> print( r.render() )
<html> Hello World! </html>

So too are block-start and block-end tags.

>>> custom_block_tags = Config( 
...   block_start_tag = 'then',
...   block_end_tag = 'end ',
... )
>>> r = RNDR( 
... "<xml>"
... "@R if 1 + 1 then R@"
... " Hello "
... "@R end if R@"
... "</xml>", custom_block_tags
... )
>>> r.render()
'<xml> Hello </xml>'


Control-structure tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, RNDR tracks control structures: every time a control structure
is initiated (e.g. ``if A == B:`` ) it will be recorded as being active until
explicitly terminated (e.g. ``endif``). This allows RNDR to determine exactly
what control structures are active or unterminated, and how to manage the
indentation of the virtual source built from the statements.

This feature can be disabled. This will result in RNDR being unable to track the
particular control structures active, and will require explicit block
management through use of the colon symbol.

The start of a block is denoted by the block_start symbol, which is found at
the end of a statement. The end of a block is denoted by the block_end symbol,
which is found at the beginning of a statement. By default, both use the colon
symbol.

>>> rc = Config( cs_tracking = False )
>>> r = RNDR( 
... "<html>"
... " Hello"
... "@R if 1+1 is 3: R@"
... " Fail"
... "@R :else: R@"
... " World! "
... "@R :end R@"
... "</html>", rc
... )
>>> print( r.render() )
<html> Hello World! </html>

This syntax is similar to that of the Templite+ templating engine.
Taking advantage of the optional start tag and end tag values,
RNDR can fully support a Templite+ template.

>>> templite_config = Config( 
...     cs_tracking = False, start_tag = '<<', end_tag='>>', 
...     output_tag_suffix = '-'
... )
>>> r = RNDR( 
... "<html>"
... " Hello"
... "<< if 1+1 is 3: >>"
... " Fail"
... "<< :else: >>"
... " World! "
... "<< :endif >>"
... "</html>", templite_config
... )
>>> print( r.render() )
<html> Hello World! </html>

"""

# [Removed: 25-03-2013]
# This usefulness of this feature is questionable and, thus, unworthy of user-level documentation.
'''
# Outputting
The method that prints rendered template content and the name and tag by
which it is called, are all configurable.

The default output method simply converts a given value to a string 
and writes it to a pseudo standard input.

There are two points of customization, the method that formats output
and the method that prints the formatted output. 
If customization is required for the outputting of content, it will
more likely be required at the point of the formatting.


>>> custom_formatter = Config( 
...     output_formatter = lambda self, x : str
... )
>>> r = RNDR( 
... "<xml>"
... "@R= 1 + 1  R@"
... "</xml>" 
... )
>>> r.render()
'<xml>2</xml>'
'''

__desc_long__ = __usage__ + __config__
__doc__ = __desc__ + __desc_long__

DEVELOPER_MODE = False

from .core import RNDR, Coder
from .base import Config
