from django.template.loaders import app_directories,filesystem
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from .core import RNDR


class DjangoRNDR( RNDR ):
    """
    A subclass of RNDR adapted for use with Django's templating system.
    """

    def render( self, context = None, *args, **kwargs ):
        """
        Transform Django's Context into a standard Python dict instance.
        """
        context_dict = {}

        if context:
            for d in context.dicts:
                context_dict.update( d )

        self.config.template_loader = lambda x: get_template( x ).render()

        return super( DjangoRNDR, self ).render( context_dict, *args, **kwargs )
        

class RNDRLoader( object ):
    """
    A standard Django template loader mixin for RNDR.
    To use, simply insert ``rndr.loaders.FileSystemLoader``
    and ``rndr.loaders.AppDirectoriesLoader`` in the
    Django project's TEMPLATE_LOADERS setting.
    """
    is_usable = True
    
    def load_template( self, template_name, template_dirs=None):
        """
        Loads templates if they contain the ".rndr." secondary 
        file extension.
        """
        if '.rndr.' in template_name:
            source, origin =  self.load_template_source( template_name )
            template = DjangoRNDR( source )
            return template, origin
        raise TemplateDoesNotExist(template_name)

class FileSystemLoader( RNDRLoader, filesystem.Loader ):
    """
    A loader that loads RNDR templates from the filesystem,
    according to the TEMPLATE_DIRS setting.
    """

class AppDirectoriesLoader( RNDRLoader, app_directories.Loader ):
    """
    A loader that loads RNDR templates from subdirectories named "templates"
    for every app listed in INSTALLED_APPS.
    """
