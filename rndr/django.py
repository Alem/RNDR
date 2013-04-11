from django.template.loaders import app_directories
from rndr import RNDR

class Loader( app_directories ):
    """
    A standard Django template loader class for RNDR.
    To use, simply insert ``rndr.django.Loader`` in your
    Django TEMPLATE_LOADERS setting.
    """
    is_usable = True
    
    def load_template( self, template_name, template_dirs=None):
        source, origin =  self.load_templat_source( template_name )
        template = RNDR( source )
        return template, origin
