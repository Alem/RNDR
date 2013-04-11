from rndr.base import Component
from rndr import exceptions

class Parser( Component ):
    """
    The Parser separates the template into its constituent Python statements
    and template content, yielding both in a step-wise manner until the end of
    the template is reached.
    """

    #: The position within the template string the parser is at 
    #: in the current parse cycle.
    index = 0
    #: The position of the start tag in current parse cycle.
    start = None
    #: The position of the end tag in current parse cycle.
    end = None
    #: The start position of the Python statement in current parse cycle.
    statement_start = None
    #: The end position of the Python statement in the current parse cycle.
    statement_end = None

    #: The character used to escape tags in the template.
    escape_char = '\\'

    def check_unterm_tag( self ):
        """
        Scans the template for any start tags that appear before an
        unterminated statement is terminated.
        """
        extra_start = self.template.find( 
                self.config.start_tag, 
                self.statement_start, self.statement_end 
        )
        if extra_start is not -1:
            raise exceptions.RNDRSyntaxError(
                                  "A second start tag was started"
                                  " before the first was closed.",
                                  self.template,
                                  self.start, self.end )
    
    def get_statement( self ):
        """
        Returns the Python statement found between the start and end tags.
        """
        return self.template[ self.statement_start : self.statement_end ]


    def seek_nonescaped( self, tag, offset ):
        """
        Returns the position of the first non-escaped instance of a tag
        relative to the offset.
        """
        pos = self.template.find( tag, offset )

        while pos > 0 and self.template[ pos - 1 ] == self.escape_char:
            pos = self.template.find( tag, pos + 1 )

        return pos


    def tag_positions( self, offset = None ):
        """
        Returns the positions of a pair of statement tags,
        if either is escaped, progress to the next tag.
        """
        offset = offset or self.index

        start = self.seek_nonescaped( 
                self.config.start_tag, offset
        )
        end   = self.seek_nonescaped( 
                self.config.end_tag, start + self.config.start_tag_len
        )
        return start, end

    def check_missing_tag( self ): 
        """
        Scans the template for missing end or start tags.
        """
        s = ( 
                ('start', self.start, self.config.start_tag_len ), 
                ('end',   self.end, self.config.end_tag_len )
        )

        # Establish and check the two cases:
        #   * Case 1: Start tag, no End tag
        #   * Case 2: End tag, no Start tag
        for a, b in ( (0,1), (1,0) ):
            if s[a][1] is not -1 and s[b][1] is -1:
                raise exceptions.RNDRSyntaxError( 
                    "Detected %s tag with no %s tag." 
                    % ( s[a][0], s[b][0] ),
                    self.template, 
                    s[a][1], 
                    s[a][1] + s[a][2]
                )

        
    def unescape( self, string ):
       """
       Replaces escaped tags with the unescaped version.
       """

       for tag in (self.config.start_tag, self.config.end_tag ):
           string = string.replace( self.escape_char + tag , tag ) 

       return string


    def set_positions( self ):
        """
        Sets the start and end positions of the current tag set, 
        and its contained statement.
        """
        self.start, self.statement_end = self.tag_positions()
        self.statement_start = self.start + self.config.start_tag_len
        self.end = self.statement_end + self.config.end_tag_len
           

    def parse( self, template = None ):
        """
        Progressively parses a template yielding an extracted Python 
        statement and the template-content preceding it each cycle.

        *Steps of the parse cycle*

        1. Establish tag+statement positions, relative to current index.
        2. If no start tag is found relative to index, 
           yield remainder and terminate, otherwise execute step 3.
        3. Collect content between current index and start tag.
        4. Collect statement and statement flags
           ( e.g. starts/ends block, output).
        5. Yield product: content, statement.
       
        
        *Diagram of an example template source.*

        ::

             0       E   A B C D             32
             ---@R--R@---@R---R@---@R--R@-----
                      |_||_____||_|      
                       F    H    G      
                  
        A. Start tag
        B. Statement start 
        C. Statement end 
        D. End tag
        E. Index (last end tag position or zero) 
        F. Cycle content
        G. Next-cycle content (controlled by SOI)
        H. Statement of interest (SOI)


        """

        self.index = 0

        if template:
            self.load_template( template )

        while True:
            self.set_positions()

            # No statements tags found beyond index. Yield remainder.
            if self.start is -1:
                yield (
                        self.unescape( self.template[ self.index: ]),
                        ''
                )
                break

            self.check_unterm_tag()

            self.check_missing_tag()

            content = self.unescape(
                        self.template[ self.index:self.start ],
            )

            # Update the current position to be the end position of the
            # current block for the next cycle.
            self.index = self.end

            yield content, self.get_statement()


class Transcriber( Component ):
    """
    The Transcriber accepts and processes the statements and content
    generated by the parser's parse cycle, writing them to a virtual code
    file with a Coder instance.
    """

    #: Tracks the control structures as they begin and terminate
    #: during the transcription process.
    active_cs = {
            "for": 0,
            "while": 0,
            "if": 0,
            "try": 0,
    }

    #: Lists the control structures recognized by RNDR.
    cs = ['for','while','if','try','else','elif','finally','except']

    def reset( self ):
        """
        Resets control-structure counts.
        """
        for i in self.active_cs:
            self.active_cs[ i ] = 0

    def get_block_states( self, statement ):
        """
        Determines if the statement begins and/or ends a statement block.
        """
        ends_block = False
        starts_block = False

        if not self.config.cs_tracking:
            starts_block = statement.endswith( self.config.block_start_tag )
            ends_block = statement.find( self.config.block_end_tag ) is 0

        else:
            if statement.endswith( self.config.block_start_tag ):

                # if (condition):
                token = statement.split()[0]

                # try:
                if token.endswith( self.config.block_start_tag ):
                    token = token[ :-1 * self.config.block_start_tag_len ]

                # is it an if, while, or for, or try
                if token in self.active_cs:
                    starts_block = True
                    self.active_cs[ token ] +=  1

                # Or an else, elif, except, or finally
                elif token in self.cs:
                    starts_block = True
                    ends_block = True

            elif statement.find( self.config.block_end_tag ) is 0:
                token = statement[ self.config.block_end_tag_len: ]

                if token in self.active_cs:
                    ends_block = True
                    self.active_cs[token] -=  1

        return starts_block, ends_block

    # FIXME: 
    # A user may attempt to define a function within a template
    # using the following approach::
    #   @R def function( parameter ): R@
    #   @R return parameter R@
    #
    # What is the intended behaviour in such cases?
    #
    # Options:
    #   * Modify ``cs`` such that 'def','class' and the sort are
    #       included, tracked and permitted.
    #   * Raise an exception if a statement contains a block_start_tag
    #       but contains no token found in ``cs``.

            
    def format_statement( 
            self, statement, starts_block, ends_block, output_short, include_directive
        ):
        """
        Formats a statement with respect to the statement flags.
        """
        # ('if True[BS]'-> 'if True:'
        if starts_block:
            statement = statement[: -1 * self.config.block_start_tag_len ] + ':'

        if ends_block:
            if starts_block:
                if not self.config.cs_tracking:
                    # '[EB]else[SB]' -> 'else:'
                    statement = statement[ self.config.block_end_tag_len:]

            # ( '[EB]' | '[EB]if' ) -> ''
            else:
                statement = ''
        
        # '[OS] var' -> 'echo( var )'
        if output_short:
            statement = "%s(%s)" % (
                    self.config.output_func_name, 
                    statement[ self.config.output_tag_suffix_len : ]
            )
        
        # '[IT] "file.rndr.html"' --> RNDR( "file.rndr.html" ).render( globals() )
        elif include_directive:
            statement = ("echo( __self.render( template = open( %s ) )) " 
                         % statement[ self.config.include_tag_suffix_len : ] )

        return statement


    def block_check( self, coder ):
        """
        Checks if control-structures/statement-blocks have been closed,
        raising a RNDRSyntaxError if they have not.
        """
        if coder.indent_level:
            if not self.config.cs_tracking:
                pluralized = 's' if coder.indent_level > 1 else ''
                raise exceptions.RNDRSyntaxError("%i statement block%s"
                                      " left unterminated." 
                                   % ( coder.indent_level, pluralized )
                )
            else:
                unterm = []
                for cs,num in list(self.active_cs.items()):
                    if num > 0:
                        pluralized = 's' if num > 1 else ''
                        unterm.append( 
                                '%i "%s" block%s' % (num,cs, pluralized )
                        )
                    
                raise exceptions.RNDRSyntaxError(
                    "%s left unterminated." % ', '.join( unterm )  

                )

    def write_statement( self, statement, coder ):
        """
        Given a statement and a coder instance, 
        writes the statement line to the coder's
        virtual source.
        """
        # Set the statement flags.
        starts_block, ends_block = self.get_block_states( statement )

        output_short = statement.find( 
                self.config.output_tag_suffix ) is 0

        include_directive = statement.find( 
                self.config.include_tag_suffix ) is 0

        statement = self.format_statement(
                statement, starts_block, ends_block, output_short, include_directive
        )

        # Write the statement.
        if starts_block and ends_block:
            coder.unindent()
            coder.write( statement )
            coder.indent()
        else:
            coder.write( statement )

            if starts_block:
                coder.indent()
            elif ends_block:
                coder.unindent()

    def align_multilined( self, statement ):
        """
        Normalizes leading whitespace in multi-lined statements.
        """
        #TODO: Review.

        nl = '\n'
        lines = statement.split( nl )

        if len(lines) > 1:
            lead = min( len(line) - len( line.lstrip() ) for line in lines if line.strip() )
            return nl.join( line[lead:] for line in lines )
        else:
            return statement.strip()
        

    def transcribe( self, coder ):
        """
        Write the parsed statements and content to virtual code file and
        compile it.
        """
        # Associates the start/end positions of segment in a template
        # to the corresponding line in the virtual source code.
        line_mappings = {}

        self.reset()

        p = Parser( template = self.template, config = self.config )

        for content, statement in p.parse():

            if content:
                printing_content = "%s( '''%s''' )" % (
                        self.config.output_func_name, content.replace("'","\\'"), 
                )
                # Single quotes (') found in the printing content are escaped
                # twice; when written to virtual source they become
                # single-escaped quotes and are consequently printed to
                # standard output as regular unescaped quotes.  This prevents
                # the accidental termination of the output function's
                # longstring literal parameter ('''%s''') by a leading or
                # ending single quote or a triple single quote template
                # content.


                content_end_pos = p.index + len( printing_content )

                coder.write( printing_content )
                line_mappings[ coder.lineno ] = p.index, content_end_pos


            statement = self.align_multilined( statement )


            if statement:
                try:
                    self.write_statement( statement, coder )
                except exceptions.RNDRIndentError as e:
                    raise RNDRSyntaxError( 
                            str(e), self.template,
                            p.start, p.end
                )
                line_mappings[ coder.lineno ] = p.start, p.end

        self.block_check( coder )
        return coder, line_mappings
