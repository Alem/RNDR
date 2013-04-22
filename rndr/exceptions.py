import sys
import rndr

class RNDRCodeCreationError( Exception ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

class RNDRRenderingError( Exception ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

    #: The start position of the exception-causing line in the template.
    start = None

    #: The end position of the exception-causing line in the template.
    end   = None

    #: Holds the statement that generated the exception.
    statement = None

    #: Holds the original template in string form.
    template = None

    #: Holds the virtual source constructed so far.
    source = None

    #: The symbol used to mark the beginning of the exception-causing
    #: line in the template.
    fault_start_symbol = '-->'

    #: The symbol used to mark the end of the exception-causing
    #: line in the template.
    fault_end_symbol = '<--'

    def fault_location( self ):
        b = self.template.source[ 0:self.start ]
        r = self.template.source[ self.end: ]
    
        up_to = lambda p,maxi=40: min( int(len(p)/2), maxi )
        b_s = up_to( b )
        r_s = up_to( r )

        self.statement = self.template.source[ self.start:self.end ]

        line =  "%s %s %s %s %s" % ( 
                b[b_s:], self.fault_start_symbol, self.statement,
                self.fault_end_symbol, r[:r_s] 
        )
        return "\n Statement: \n %s" % line


    def __init__( 
            self, message, template = None,
            start = None, end = None, source = None,
            fault_start_symbol = None, fault_end_symbol = None
        ):

        if fault_start_symbol:
            self.fault_start_symbol = fault_start_symbol
        if fault_end_symbol:
            self.fault_end_symbol = fault_end_symbol

        self.start = start
        self.end = end
        self.template = template
        self.source = source

        if None not in (start, end, template):
            message += self.fault_location()

        if rndr.DEVELOPER_MODE:
            message += '\n\nStart: %s\nEnd: %s' % ( self.start, self.end )
            if self.statement:
                message += '\nStatement-length: %d' % len( self.statement )
            if source:
                message += '\n\nVirtual Source:\n' + source

        self.message = message

        Exception.__init__(self,message)

class RNDRSyntaxError( RNDRRenderingError ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

class RNDRExceptionWrapper( RNDRRenderingError ):
    """
    Extracts the error message from the original exception which
    occurred in the parser generated code. 
    Serves to distinguish the errors raised by parser generated code
    from regular application code.
    """
    #: The original exception raised.
    exception = None

    #: The line number in the virtual source at which the original
    #: exception occurred.
    lineno = None

    def set_lineno( self ):
        self.lineno = self.exception.lineno

    def __init__( self, exception,
            template = None, source = None, line_mappings = None ):

        self.exception = exception
        
        message = "%s  (%s)" % ( str(exception),
                exception.__class__.__name__)

        self.set_lineno()

        start, end = None, None

        if line_mappings.get( self.lineno ):
            start, end = line_mappings[ self.lineno ]

        # Determine start and end points from exception line+offset and
        # line_mappings
        RNDRRenderingError.__init__( 
                self, message, template, start, end, source 
        )

class RNDRCompiletimeError( RNDRExceptionWrapper ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

class RNDRRuntimeError( RNDRExceptionWrapper ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

    def set_lineno( self ):
        """
        Cycles through the traceback objects and retrieves the line number
        of the last one available.
        """
        e_type, e_obj, e_tb = sys.exc_info()

        while e_tb.tb_next:
            e_tb = e_tb.tb_next

        self.lineno = e_tb.tb_lineno

        
class RNDRIndentError( IndentationError ):
    """
    Raised when a syntax error is found within a RNDR statement.
    """

class RNDRConfigurationError( ValueError ):
    """
    Raised when RNDR has inappropriate or impossible configurations.
    """

class InvalidArgumentValue( ValueError ):
    """
    Raised when a RNDR interface is provided an invalid
    value for an argument or option.
    """
