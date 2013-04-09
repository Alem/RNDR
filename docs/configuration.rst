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

