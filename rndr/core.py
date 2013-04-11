import sys
from ast import PyCF_ONLY_AST

from rndr import exceptions
from rndr.parse import Transcriber
from rndr.base import Component
from cStringIO import StringIO

class Coder( object ):
    """
    The Coder allows the construction and execution of Python code, 
    within Python code. 
    A simple interface is provided for writing, compiling, executing, and
    evaluating Python code along with capturing any output sent to 
    the Standard output stream.

    >>> coder = Coder()
    >>> coder.write("if True:") \
    ...      .indent() \ 
    ...      .write("print( 'Hello world!' )") \ 
    ...      .execute() 
    Hello world!
    >>> coder.capture().rstrip()
    'Hello world!'
    >>> print( coder.source )
    if True:
        print( 'Hello world!' )
    """

    #: Holds the virtual source code in string form.
    source = ''

    #: Holds any printed output in string form.
    output = ''

    #: Holds the code object generated from compiling the virtual source.
    code = None

    #: Reports the current level of indentation in the virtual source code.
    indent_level = 0

    #: Reports whether the virtual source has been changed since the last 
    #: compilation.
    code_recent = False

    #: The character(s) used to indent source lines. 
    #: Set to four spaces by default.
    indent_char = '    '

    def get_lineno( self ):
        return len( self.source.split( '\n' ) )

    #: Reports the number of the last line of virtual source.
    lineno = property( get_lineno )


    def indent( self ):
        """
        Increments the indentation level of the source code.
        """
        self.code_recent = False
        self.indent_level = self.indent_level + 1

        return self

    def unindent( self ):
        """
        Decrements the indentation level of the source code.        
        """
        self.code_recent = False
        self.indent_level = self.indent_level - 1

        if self.indent_level < 0:
            raise exceptions.RNDRIndentError("No statement block to terminate")

        return self

    def delete( self, line = -1 ):
        """
        Remove the line specified from the source;
        defaults to the last line.
        """
        self.code_recent = False

        nl = '\n'
        lines = self.source.split( nl )
        lines.pop( line )
        self.source = nl.join(lines)

        return self


    def write( self, statement, on_newline = True ):
        """
        Writes the given statement to the source.
        """
        self.code_recent = False

        line_delimiter = '' if not on_newline or not self.source else '\n'

        indent = self.indent_level * self.indent_char 

        self.source += line_delimiter + indent + statement

        return self

    def syntax_tree( self ):
        """
        Generates a abstract syntax tree for the current source code.
        """
        return self.internal_compile( flags = PyCF_ONLY_AST )

    def check_syntax( self ):
        """
        Checks the syntax of the current source code.
        """
        return self.syntax_tree()

    def internal_compile( self, flags = 0 ):
        """
        Compiles the held source code and returns the resultant code object.
        """
        return compile( 
                    self.source,
                    "<virtual_executable: %r>" % self.source[-15:],
                    'exec',
                    flags
        )

    def compile( self ):
        """
        Compiles the source code and sets the code recency flag.
        """
        if not self.code_recent:
            self.code =  self.internal_compile()

        self.code_recent = True
        return self.code

    def erase( self ):
        """
        Erases the source, output, and code; and resets state 
        tracking attributes.
        """
        self.source = ''
        self.output = ''
        self.code = None
        self.lineno = 0
        self.indent_level = 0
        self.code_recent = True

        return self

    def evaluate( self, globals = {}, locals = {} ):
        """
        Evaluates the source code and returns the result.
        """
        return eval( self.compile() , globals, locals )

    def execute( self, globals = {}, locals = {} ): 
        """
        Executes the source code.
        """
        exec( self.compile(), globals, locals )

    def capture( self, globals={}, locals={} ):
        """
        Captures data sent to standard output and internalizes it in
        string form.
        """
        stdout_bak = sys.stdout

        sys.stdout = StringIO()

        try:
            self.execute( globals, locals )
            self.output = sys.stdout.getvalue()
        finally:
            sys.stdout = stdout_bak

        return self.output

                

class RNDR( Component ):
    """
    RNDR takes a template in the form of string or file, 
    along with any associated context variables, and returns the
    rendered result. 

    >>> tpl = 'Hello @R= name R@!'
    >>> r = RNDR( tpl )
    >>> r( name = 'world')
    'Hello world!'
    """

    #: Holds the Coder instance.
    coder = None

    #: Holds the context variables
    context = {}

    def __init__( self, *args, **kwargs ):
        super( RNDR, self ).__init__( *args, **kwargs )
        self.context[ self.config.output_func_name ] = self.config.output_func
        self.context[ '__self' ] = self

    def render( self, context = None, template = None ):
        """
        Renders the content, using any given context as the namespace for
        the compiled RNDR code.
        """

        if template:
            self.load_template( template )

        if not self.template:
            raise exceptions.RNDRConfigurationError(
                "Could not render template content as no template was"
                " provided."
            )


        if context:
            self.context.update( context )

            if context.get( self.config.output_func_name ):
                raise exceptions.RNDRConfigurationError(
                        "The context key '%s' is already mapped"
                        " to the output function, as specified by the"
                        " configuration object."
                        % ( self.config.output_func_name) )


        tr = Transcriber( template = self.template, config = self.config )

        self.coder = Coder()

        # Transcribes statements from the template to the coder source 
        # and provides the mapping.
        self.coder, line_mappings = tr.transcribe( self.coder )

        try:
            self.coder.compile()
        except Exception as e:
            raise exceptions.RNDRCompiletimeError( 
                    e, self.template, self.coder.source, line_mappings
            )

        try:
            return self.coder.capture( self.context )
        except Exception as e:
            raise exceptions.RNDRRuntimeError( 
                    e, self.template, self.coder.source, line_mappings
            )

    def render_with( self, **kwargs ):
        return self.render( context = kwargs )

    __call__ = render_with
