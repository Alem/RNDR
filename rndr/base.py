import sys
from rndr import exceptions

class TemplateHandling( object ):
    """
    The TemplateHandling mix-in grants simple and uniform 
    validation and loading of templates.
    """

    #: Holds the source template in string form.
    template = None

    def load_template( self, template ):
        """
        Stores the template string or file content upon successful
        type-validation.
        """
        if isinstance( template, file ):
            self.template = template.read()
            template.close()
        elif isinstance( template, basestring ):
            self.template = template
        else:
            raise exceptions.RNDRConfigurationError(
                    "Expected a string or"
                     " file based template, received '%s'"
                     " object instead." % template.__class__.__name__ 
            )

class Config( object ):
    """
    The Config object serves to encapsulate configuration settings for 
    all RNDR Components.
    """

    #: The tag that marks the beginning of a Python statement.
    start_tag = '@R'

    #: The tag that marks the end of a Python statement.
    end_tag   = 'R@'

    #: The tag that marks the beginning of a Python statement block.
    block_start_tag = ':'

    #: The tag that marks the end of a Python statement block.
    block_end_tag   = 'end'

    #: If set to true, certain control structures will have their initiation
    #: and termination tracked by RNDR.
    cs_tracking = True

    #: The name of the output function used within RNDR templates.
    output_func_name = "echo"

    #: The suffix that when appending the start_tag, results in the named file
    #: being included into the template and rendered.
    #: e.g. Using default settings, 
    #: ``@R< "filename.rndr.html" R@`` will include and render the contents of
    #: filename.rndr.html
    include_tag_suffix = '<'

    #: The function that loads a template to be included given the filepath.
    #:
    #: The default implementation does nothing.
    template_loader = lambda self,x : open( x )
        

    #: The suffix that when appending the start_tag, results in the enclosed 
    #: statement being passed as a parameter to the output function.
    #: e.g. Using default settings, 
    #: ``@R= variable R@`` is equivalent to ``@R echo( variable ) R@``.
    output_tag_suffix = '='

    #: The function that formats the variable before it is printed by the
    #: output function.
    #:
    #: The default implementation of the output function expects a ``str``
    #: instance, thus the formatter should return such.
    output_formatter = lambda self,x : str( x )
        
    def output_func( self, value ):
        """
        Writes the given value to standard output.
        """
        sys.stdout.write( self.output_formatter(value) )


    def __init__( self, **kwargs ):
        """
        Initializes the Config object.
        All keyword parameters passed on construction will be used to
        initialize configuration settings by the same name.
        """
        for key in kwargs:
            if hasattr(self, key ):
                setattr(self, key, kwargs[key])
            else:
                raise exceptions.RNDRConfigurationError(
                    "'%s' is not a recognized configuration setting." % key 
                )

        if not ( self.cs_tracking or kwargs.get('block_end_tag')):
            self.block_end_tag = ':'

        for i in ('start_tag','end_tag','block_start_tag','block_end_tag',
                  'output_tag_suffix','include_tag_suffix'):
            setattr( self, i + '_len', len( getattr( self, i ) ) )

class Configurable( object ):
    """
    The Configurable mix-in grants simple and uniform 
    validation and loading of the configuration object,
    a Config instance.
    """

    #: Holds an instance of the _`RNDR.base.Config` class. 
    config = None

    def load_config( self, config = None ):
        """
        Instantiates and stores a configuration object if none
        is provided. Otherwise, it stores the given configuration object
        upon successful type-validation.
        """
        if not config:
            config = Config()
        elif not isinstance( config, Config ):
            raise exceptions.RNDRConfigurationError(
                    "Expected a Config object, recieved a '%s'"
                    " object instead." % config.__class__.__name__ 
            )

        self.config = config
        

class Component( Configurable, TemplateHandling ):
    """
    The Component class serves as an abstract / non-instantiated base
    class providing a common interface for configuration and 
    template-loading.
    """

    def __init__( self, template = None, config = None ):
        """
        Initialize or load the configuration settings, and load the given
        template.
        """
        if template:
            self.load_template( template )

        self.load_config( config )
