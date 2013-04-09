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
