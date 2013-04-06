import sys
import argparse
import json

import doctest
import unittest

import rndr

class ConsoleInterface( object ):

    def set_options( self, parser ):
        """
        Configures parser for the command-line arguments to be parsed.
        """
        parser.add_argument('template', nargs='?', 
                type=argparse.FileType('r'), default=sys.stdin,
                metavar='<template file>',
                help="The template file marked-up with RNDR statements."
                     " Defaults to Stdin when no value is provided.")

        parser.add_argument('-c','--context', type=argparse.FileType('r'),
                help="The file containing RNDR context variables in the"
                     " form of a Python dictionary expression or a JSON array.",
                        metavar="<context file>", dest="context" )
                             

        parser.add_argument('output', nargs='?', 
                type=argparse.FileType('w'), default=sys.stdout,
                metavar='<output file>',
                help="The file to write the rendered content to."
                     " Defaults to Stdout when no value is provided.")


        if rndr.DEVELOPER_MODE is True:
            parser.add_argument("-d","--doctests",   dest ='doctest',
                action='store_true', help ="Test the usage examples in the user-documentation." )
            parser.add_argument("-u","--unittests",   dest ='unittest',
                action='store_true', help ="Execute the entire test suite." )
            parser.add_argument("--verbose",  dest ='verbose',
                action='store_true', help ="Relentlessly vomit text whilst doing so." )
            parser.add_argument("-g","--graphical",  dest ='graphical',
                action='store_true', help ="Launch a half-assed GUI.")

        return parser

    def get_parser( self ):
        """
        Construct and return the argument parser.
        """
        version = "RNDR " + rndr.__version__ 
        parser = argparse.ArgumentParser( 
                prog = rndr.__prog__,
                version = version, 
                description = rndr.__desc__,
                fromfile_prefix_chars = ['@'],
                formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        return self.set_options( parser )
    

    def execute_tests(
            self, doctests = False, unittests = True, verbose = False 
        ):
        """
        Run the specified test types and exits the program.
        """
        if doctests:
            doctest.testmod( rndr, verbose = verbose )
            # This file is created by a doctest contained in
            # the 'Templates and Context' section in the rndr.__usage__
            # string.
            # The doctests in this section serve more as user-targetted 
            # illustrations than actual tests, so post-test clean-up 
            # and other procedures specific to testing should be performed
            # outside the doctest.
            # If ever that docttest stops creating this file, this operation
            # will fail. Also, if you are unfortunate enough to execute this
            # in a directory with a file named 'test.xml', it will be 
            # destroyed; a check for the existence of the file could be
            # performed, but who cares?
            import os
            os.remove( 'test.xml' )

        if unittests:
            verbosity = 0
            if verbose:
                verbosity = 3

            unittest.main( module = 'rndr.tests', argv = [ rndr.__prog__ ], verbosity = verbosity )


    def get_context( self, context_file ):
        """
        Builds the context dictionary from the JSON
        array or Python dictionary expression.
        """
        context_str = context_file.read()
        context_file.close()

        # Tries JSON-decoding the file content, 
        # if this fails it is presumed to be a Python dictionary 
        # expression and evaluated.
        #
        # FIXME: Evaluating file content as a fall-back mechanism
        # for failed JSON-decoding is a fundamentally flawed approach.
        # User should specify whether context is JSON or Python.
        try:
            jd = json.JSONDecoder()
            context = jd.decode( context_str )
        except ValueError:
            context = eval( context_str )

        return context 

    def run( self, args = None, print_outut = True ):
        """
        Parse the command line arguments and run the program.
        """
        parser = self.get_parser()
        namespace = parser.parse_args( args )

        if rndr.DEVELOPER_MODE:
            if namespace.doctest or namespace.unittest:
                self.execute_tests( 
                        namespace.doctest, namespace.unittest,
                        namespace.verbose
                )
                parser.exit()

            if namespace.graphical:
                app = wx.App(False)
                win = Window( None )
                app.MainLoop()


        r = rndr.RNDR( namespace.template )
        context = {}

        if namespace.context:
            context = self.get_context( namespace.context )

        output = r.render( context = context )

        if print_outut:
            print( output )

        return output

import wx
class Window(wx.Frame):
    # Develop this or delete it.

    panel = None
    button = None
    result  = None

    sizer = None

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.Title = "RNDR Template Renderer"
        self.panel = wx.Panel(self)
        self.button = wx.Button(
            self.panel, label="Render"
        )
        self.command = wx.TextCtrl(
            self.panel, style=wx.TE_MULTILINE
        )
        self.result = wx.TextCtrl(
            self.panel, style=wx.TE_MULTILINE
        )

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.command, 1, wx.EXPAND)
        self.sizer.Add(self.button, 0, wx.EXPAND)
        self.sizer.Add(self.result, 1, wx.EXPAND)

        self.command.SetValue("dir")
        self.button.Bind(wx.EVT_BUTTON, self.CallCommand)

        self.panel.SetSizerAndFit(self.sizer)  
        self.Show()

    def CallCommand(self, e):
        p = rndr.RNDR(self.command.GetValue())()
        self.result.SetValue( p )
