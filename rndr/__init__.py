__alias__   = "RNDR"
__prog__    = "rndr"
__author__  = "Z. Alem"
__licence__ = "MIT License"
__version__ = "1.1.5"
__home__    = "http://rndrengine.com"
__repo__    = "https://github.com/Alem/RNDR.git"
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

>>> f = open('test.rndr.xml','w')
>>> r = f.write( 
... "<xml>"
... "@R= 1+1 R@"
... "</xml>" 
... )
>>> f.close()
>>> r = RNDR( open('test.rndr.xml') )
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


File and Template Inclusion
~~~~~~~~~~~~~~~~~~~~~~~~~~~

RNDR also supports the inclusion of files and other RNDR templates into a
template.
The content of a file inclusion statement takes the form: ::

    <include_tag_suffix> "filename" | filename_variable

The ``include_tag_suffix`` is the tag leading the ``start_tag`` of a
statement. By default, the ``include_tag_suffix`` is an opening angle bracket
('<').  ::

    @R< "filename" R@
    @R< filename_variable R@

Templates included into other templates will share the same
context variables.

To provide a complete illustration:

>>> with open('plain.txt','w') as plain, open('renderable.rndr.txt','w') as renderable:
...     plain.write(
...     " Hello World. "
...     )
...     renderable.write(
...     "@R if name: R@"
...     "Hello @R= name R@."
...     "@R endif R@"
...     )
>>> r = RNDR(
... "<x>"
... "@R< 'plain.txt' R@"
... "@R< 'renderable.rndr.txt' R@"
... "</x>"
... )
>>> print( r.render( context = {'name':'Moe'} ) )
<x> Hello World. Hello Moe.</x>


Django Integration
~~~~~~~~~~~~~~~~~~

Some users may want to integrate RNDR into their Django projects. This can be
done quite easily: simply insert the line ``"rndr.loaders.RNDRLoader"`` into the
``TEMPLATE_LOADERS`` list in your projects settings.py file.
Note that the RNDR template loader will **only** load templates that contain the 
nested/secondary extension '.rndr' (e.g. template.rndr.html ). ::

   TEMPLATE_LOADERS = (
     'rndr.loaders.FileSystemLoader',
     'rndr.loaders.AppDirectoriesLoader',
      ...
   )


Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

RNDR also includes a very simple console interface for rendering template
in a command-line environment.

There are two positional arguments that may be passed. The first is the path of
the template file and the second is the file to which rendered content will
be written to. ::
    
    $ python -m rndr template.rndr.html rendered.html

They default to the standard input and output streams respectively, meaining
they can be used in pipes and standard stream redirections. ::

    $ echo "@R if True: R@ Hello @R endfor R@" | python -m rndr
    Hello

    $ echo "@R for i in (1,2,3): R@ Hello @R endfor R@" | python -m rndr  > rendered.html

One may also provide the context variables for a template by creating a
file containing an evaluatable Python dictionary expression ( e.g.
``{'context_var':123}`` ) or a JSON array (e.g. ``{ "context_var":123 }`` ) and providing
its file path as the value for the ``-c`` or ``--context`` arguments. ::

    python -m rndr template.rndr.html rendered.html -c context.py

Finally, one may retrieve the version number by passing the ``-v`` 
and ``--version`` arguments, or the help message via ``-h`` and ``--help``.

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
management through use of the ``block_start_tag`` and ``block_end_tag``
symbols.

The start of a block is denoted by the block_start symbol, which is found at
the end of a statement. The end of a block is denoted by the block_end symbol,
which is found at the beginning of a statement. By default, both use the colon (':').

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
Taking advantage of the configurable ``start_tag`` and ``end_tag`` values,
RNDR can fully support a Templite+ template.

>>> templite_config = Config( 
...     cs_tracking = False, start_tag = '<<', end_tag='>>', 
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
