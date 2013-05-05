# -*- coding: utf-8 -*-
#TODO: Add tests for the Django template loaders.
#TODO: Document test methods.

import sys
import os
import unittest
from rndr import exceptions
from rndr.base import Config
from rndr.core import RNDR
from rndr.interfaces import ConsoleInterface

class RNDRTestCase( unittest.TestCase ):
    """
    The base class for all test cases in the rndr module.
    Provides an instance of RNDR, a base template, and methods
    for simplified configuration and assertions.
    """

    def setUp( self ):
        self.r = RNDR()

        self.base_tpl = "<x>%s</x>"
        self.configure()

    def render( self, template, context = None ):
        self.r.load_template( template )
        return self.r.render( context = context )

    def assertRendersAs( self, template, expect, context = None ):
        rt = self.render( template, context )
        self.assertEqual( rt, expect )

    def configure( self ):
        pass

class OutputTestCase( RNDRTestCase ):
    """
    Tests the printing of Python variables into a template.
    """

    def test_output( self ):
        ot = (
                "@R echo('Hi ') R@"
                "@R echo( var ) R@"
                "@R= 'Hi ' R@"
                "@R= var R@"
            )
        t = self.base_tpl % ot 

        expect = "<x>Hi Hi Hi Hi </x>"
        msg = "Hi "
        self.assertRendersAs(t, expect, {'var':msg} )

class EscapedStatementsTestCase( RNDRTestCase ):
    """
    Tests the bypassing and unescaping of escaped RNDR statements.
    """

    def test_escaping( self ):
        ets = [
                "\@R  Escaped start tag",
                "\R@  Escaped end tag",
                "\@R= Escaped output tag",
                "\@R  Escaped statement \@R",
                "\@R= Escaped output statement \@R"
        ]
        for et in ets:
            expect = et.replace('\\','')
            self.assertRendersAs( et, expect )
    

class ContextInjectionTestCase( RNDRTestCase ):
    """
    Tests the functionality of context variables injected into templates.
    """

    def test_variable( self ):
        ct = (
            "@R if var: R@"
            "Hi"
            "@R endif R@"
        )
        t = self.base_tpl % ct
        expect = "<x>Hi</x>"
        self.assertRendersAs( t, expect, {'var':True} )

    def test_function(  self ):
        ct = (
                "@R if is_hello('hello'): R@"
                "Hi"
                "@R endif R@"
        )
        t = self.base_tpl % ct
        expect = "<x>Hi</x>"
        self.assertRendersAs( t, expect, {'is_hello':lambda x: x is "hello"} )


    def test_class(  self ):
        ct = (
                "@R if obj.method(): R@"
                "Hi"
                "@R endif R@"
        )
        t = self.base_tpl % ct
        expect = "<x>Hi</x>"

        class obj:
            method = lambda self: True

        self.assertRendersAs( t, expect, {'obj': obj() } )

class FileInclusionTestCase( RNDRTestCase ):
    """
    Tests functionality of include directive.
    """

    file_path_1 = "file.rndr.html"
    file_path_2 = "file2.rndr.html"
    test_dir    = 'test_tpls/'


    def setUp( self ):
        super( FileInclusionTestCase, self ).setUp()

        self.full_path_1 =  self.test_dir + self.file_path_1
        self.full_path_2 =  self.test_dir + self.file_path_2

        os.mkdir( self.test_dir )

    def tearDown( self ):
        super( FileInclusionTestCase, self ).tearDown()
        for i in (self.full_path_1, self.full_path_2):
            if os.path.exists( i ):
                os.unlink( i )
        os.rmdir( self.test_dir )

    def test_plain_inclusion( self ):
        """
        Tests inclusion of a plain text file.
        """
        with open( self.full_path_1, 'w' ) as f:
            f.write("Hello")

        tpl = "@R< '%s' R@ World" % self.full_path_1
        
        self.assertRendersAs( tpl, "Hello World" )

    def test_renderable_inclusion( self ):
        """
        Tests inclusion of a RNDR template file.
        """

        with open( self.full_path_1, 'w' ) as f:
            f.write("@R if True:R@"
                    "Hello"
                    "@R endif R@")

        tpl = "@R< '%s' R@ World" % self.full_path_1
        
        self.assertRendersAs( tpl, "Hello World" )
           

    def test_renderable_inclusion_with_context( self ):
        """
        Tests inclusion of a RNDR template file with shared context.
        """

        with open( self.full_path_1, 'w' ) as f:
            f.write("@R if True:R@"
                    "Bye @R= name R@"
                    "@R endif R@")

        tpl = "Hi @R= name R@. @R< '%s' R@" % self.full_path_1
        
        self.assertRendersAs( tpl, "Hi Moe. Bye Moe", context = { 'name': 'Moe' } )

    def test_inclusion_path_relativity( self ):
        """
        Tests file inclusion is relative to the template.
        """
        with open( self.full_path_1, 'w' ) as f:
            f.write("@R if True:R@"
                    "Bye @R= name R@"
                    "@R endif R@")

        with open( self.full_path_2, 'w' ) as f:
            f.write("Hi @R= name R@. @R< '%s' R@" % self.file_path_1 )

        with open( self.full_path_2, 'r' ) as f:
            self.assertRendersAs( f, "Hi Moe. Bye Moe", context = { 'name': 'Moe' } )
        
class MiscUseTestCase( RNDRTestCase ):

    def test_multiline_statements( self ):
        """
        Tests support for multi-lined statements within templates.
        """

        indented = (
            """@R 
            if False:
                print "Fail"
            elif 1 is 3:
                print "Fail"
            else:
                print "Hello"
            R@"""
        )
        self.assertRendersAs( indented, "Hello\n" )

class CSTestCase( RNDRTestCase ):
    """
    Tests the functionality of various Python control structures
    within templates.
    """

    cs_tracking = True

    def configure( self ):
        self.r.load_config( 
                Config( cs_tracking = self.cs_tracking )
        )

    def test_if(  self ):
        endif = 'endif'
        _else = 'else'
        _elif = 'elif'
        if not self.cs_tracking:
            endif = ':' + endif
            _else = ':' + _else
            _elif = ':' + _elif

        if_cs = (
              "@R if 1+1 is 2: R@"
              "Hi"
              "%s"
              "@R " + endif + " R@")

        if_else_cs = (
                "@R if 1+1 is 3: R@"
                "Fail"
                "@R " + _else +": R@"
                "Hi"
                "%s"
               "@R "+ endif +" R@") 

        if_elif_else_cs = (
                "@R if 1+1 is 3: R@"
                "Fail"
                "@R " + _elif + " 1+1 is 2: R@"
                "Hi"
                "%s"
                "@R " + _else +": R@"
                "Fail"
                "@R " + endif + " R@") 

        s_if = if_cs % '' 
        s_if_else = if_else_cs % '' 
        s_if_elif_else = if_elif_else_cs % '' 

        n_if = if_cs % s_if
        n_if_else = if_else_cs % s_if_else
        n_if_elif_else = if_elif_else_cs % s_if_elif_else


        t_if = self.base_tpl % s_if
        t_if_else = self.base_tpl % s_if_else
        t_if_elif_else = self.base_tpl % s_if_elif_else

        t_nested_if = self.base_tpl % n_if
        t_nested_if_else = self.base_tpl % n_if_else
        t_nested_if_elif_else = self.base_tpl % n_if_elif_else 
        
        expect = "<x>Hi</x>"
        nested_expect = "<x>HiHi</x>"

        self.assertRendersAs( t_if, expect )
        self.assertRendersAs( t_if_else, expect )
        self.assertRendersAs( t_if_elif_else, expect )

        self.assertRendersAs( t_nested_if, nested_expect )
        self.assertRendersAs( t_nested_if_else, nested_expect )
        self.assertRendersAs( t_nested_if_elif_else, nested_expect )
        

    def test_for(  self ):
        endfor = 'endfor'
        if not self.cs_tracking:
            endfor = ':' + endfor

        for_cs =(
                "@R for i in [0,1]: R@"
                "Hi "
                "%s"
                "@R " + endfor + " R@")

        expect = "<x>Hi Hi </x>"
        nested_expect = "<x>Hi Hi Hi Hi Hi Hi </x>"

        s_for = for_cs % ''
        n_for = for_cs % s_for 

        t_for = self.base_tpl % s_for
        t_nested_for = self.base_tpl % n_for 

        self.assertRendersAs( t_for, expect )
        self.assertRendersAs( t_nested_for, nested_expect )

    def test_while(  self ):

        endwhile = 'endwhile'
        if not self.cs_tracking:
            endwhile = ':' + endwhile

        while_cs = (
                "@R %(var)s=0 R@"
                "@R while %(var)s < 2: R@"
                "%(content)s"
                "Hi "
                "@R %(var)s+= 1 R@"
                "@R "+endwhile + " R@" 
        )
        s_while = while_cs % {'content':'','var':'i'} 
        n_while = while_cs % {'content': s_while,'var':'a'} 

        t_while = self.base_tpl % s_while
        t_nested_while = self.base_tpl % n_while

        expect = "<x>Hi Hi </x>"
        nested_expect = "<x>Hi Hi Hi Hi Hi Hi </x>"
        self.assertRendersAs( t_while, expect )
        self.assertRendersAs( t_nested_while, nested_expect )

    def test_try(  self ):

        endtry = 'endtry'
        _except = 'except'
        if not self.cs_tracking:
            endtry = ':' + endtry
            _except = ':' + _except

        try_cs = (
                "@R try: R@"
                "@R 1/0 R@ "
                "@R " + _except + " Exception as e: R@"
                "Hi "
                "%s"
                "@R " + endtry + " R@")

        s_try = try_cs % ''
        n_try = try_cs % s_try

        t_try =  self.base_tpl % s_try
        t_nested_try =  self.base_tpl % n_try

        expect = "<x>Hi </x>"
        nested_expect = "<x>Hi Hi </x>"

        self.assertRendersAs( t_try, expect )
        self.assertRendersAs( t_nested_try, nested_expect )

class NoTrackingCSTestCase( CSTestCase ):
    """
    Tests functionality of control structures in the template when 
    they are untracked.
    """

    cs_tracking = False

import re
class MalformedTemplatesTestCase( RNDRTestCase ):
    """
    Tests the functionality of RNDR exception types.
    """

    def assertExc( self, exception, message, template, 
            start = None, end = None, context = None ):
        try:
            try:
                self.render( template, context )
            except Exception as e:
                self.assertIsInstance( e, exception )
                self.assertNotEqual( re.findall( message, str(e) ), [] )

                if None not in (start, end):
                    self.assertEqual( e.start, start )
                    self.assertEqual( e.end, end )

        except AssertionError as ae:
            m = "%s \n\n%s\n%s\n %s" % ( 
                    str(ae), "Original Exception:",'-'*20, e.message
            )
            raise AssertionError( m )

    
    def test_unterm_blocks( self ):
        self.assertExc( 
                exceptions.RNDRSyntaxError, 
                '"if" block left unterminated',
                "<x> @R if True: R@"
                " Hello world!",
        )
        self.assertExc( 
                exceptions.RNDRSyntaxError,
                '1 "for" block, 1 "if" block left unterminated',
                "<x> @R if True: R@"
                    "<x> @R for i in (0,2): R@"
                    " Hello world!",
        )    
    def test_extra_start( self ):
        self.assertExc( 
                exceptions.RNDRSyntaxError, 
                "tag was started before .* closed",
                "<x> @R @R if True: R@", start = 4, end = 21
                #01234567801234567890123456789
        )


    def test_runtime_errors( self ):
        self.assertExc( 
                exceptions.RNDRRuntimeError, 
                '(ZeroDivisionError)',
                "<x> @R a = 1/0 R@", start = 4, end = 17
                #01234567801234567890123456789
        )
        self.assertExc( 
                exceptions.RNDRRuntimeError, 
                '(NameError)',
                "<x> @R= undefined_var R@", start = 4, end = 24
                #01234567801234567890123456789
        )

    def test_compiletime_errors( self ):
        self.assertExc( 
                exceptions.RNDRCompiletimeError, 
                '(SyntaxError)',
                "<x> @R if not is backwards R@ ", start = 4, end = 29
                #01234567801234567890123456789
        )

class ConfigurationsTestCase( RNDRTestCase ):
    """
    Tests support for various configuration profiles.
    """

    def test_tag_configurations( self ):
       id_config = Config( 
          start_tag = '||', end_tag='||' 
       )
       id_tpl = (
            "<html>"
            " Hello"
            "|| if 1+1 is 3: ||"
            " Fail"
            "|| else: ||"
            " World! "
            "|| endif ||"
            "</html>"
        )
       self.r.load_config( id_config )
       self.assertRendersAs( id_tpl, "<html> Hello World! </html>" )

       block_config = Config( 
               block_start_tag = 'then', block_end_tag='end ' 
       )
       id_tpl = (
            "<html>"
            " Hello"
            "@R if 1+1 is 3 then R@"
            " Fail"
            "@R else then R@"
            " World! "
            "@R end if R@"
            "</html>"
        )
       self.r.load_config( block_config )
       self.assertRendersAs( id_tpl, "<html> Hello World! </html>" )
        

if sys.version_info < ( 3, ):

    class UnicodeTestCase( RNDRTestCase ):
        """
        Tests support for templates and context containing Unicode
        characters. 
        ( Only applies to Python versions < 3 )
        """
        enc_char = unichr(200).encode('latin1')
        filename = os.path.dirname( __file__ ) + '/unicode.tpl'

        def tearDown( self ):
            super( UnicodeTestCase, self ).tearDown()
            if os.path.exists( self.filename ):
                os.remove( self.filename )


        def test_unicode_template( self ):

            self.assertRendersAs( 
                    "@R if True: R@"
                    + self.enc_char +
                    "@R endif R@",
                    self.enc_char
            )

            self.assertRendersAs( 
                    "@R if True: R@"
                    "Hello الشفرة"
                    "@R endif R@",
                    "Hello الشفرة"
            )

            with open( self.filename,'w') as uf:
                uf.write( 
                    "@R if True: R@"
                    "Hello الشفرة"
                    "@R endif R@",
                )

            with open( self.filename,'r') as uf:
                self.assertRendersAs( 
                        uf,
                        "Hello الشفرة"
                )

        def test_unicode_context( self ):

            self.assertRendersAs( 
                    "@R if True: R@" 
                    "Hello "
                    "@R= var R@"
                    "@R endif R@",
                    "Hello %s" % self.enc_char, context = {'var': self.enc_char}
            )

            self.assertRendersAs( 
                    "@R if True: R@"
                    "Hello "
                    "@R= var R@"
                    "@R endif R@",
                    "Hello الشفرة", context = {'var':'الشفرة'}
            )


import os
class CLITestCase( RNDRTestCase ):
    """
    Tests functionality of command-line interface.
    """
    tpl_filename  = 'test.tpl'
    ctxt_filename = 'test.py'

    def execute( self, template = '', context = '' ):
        args = []

        with open( self.tpl_filename, 'w' )  as tpl_file:
            tpl_file.write( template )

        args.append( self.tpl_filename )

        if context:
            with open( self.ctxt_filename, 'w' )  as ctxt_file:
                ctxt_file.write( context )
                args += [ "-c", self.ctxt_filename ]
       
        return ConsoleInterface().run( args, print_outut = False )

    def assertExecYields( self, template, expect, context = '' ):
        result = self.execute( template, context )
        self.assertEqual( result, expect )
        self.cleanup()

    def cleanup( self ):
        for i in ( self.tpl_filename, self.ctxt_filename ):
            if os.path.exists( i ):
                os.unlink( i )

    def test_template_rendering( self ):
        template =(
                "@R if True: R@"
                "Hello world!"
                "@R endif R@"
        )
        expect = "Hello world!"
        self.assertExecYields( template, expect )

    def test_context_injection( self ):
        template = "@R=var R@ world!"

        json_ctxt = '{ "var":"hello" }'
        expect = "hello world!"

        self.assertExecYields( template, expect,
                                context = json_ctxt )

        py_dic_exp_ctxt = "{ 'var' : 'hello' }"
        self.assertExecYields( template, expect, 
                                 context = py_dic_exp_ctxt )


