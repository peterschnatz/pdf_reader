from itertools import groupby
from operator import itemgetter
import re

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys, getopt

class pdfNumberFinder():
    def __init__(self,
                 pdf_directory: str = None,
                 pdf_file: list = None,
                 pages: list = None
                 ):
        assert pdf_directory or pdf_file, (
            "ValueError: Class instance requires pdf_directory or pdf_file to be defined."
        )

        if pdf_directory:
            assert isinstance(pdf_directory, str), (
                "TypeError: Expecting pdf_directory to be of type string."
            )
            if pdf_directory[-1] != "/":
                self.pdf_directory = pdf_directory + "/"
            else:
                self.pdf_directory = pdf_directory
        else:
            self.pdf_directory = pdf_directory

        if pdf_file:
            assert isinstance(pdf_file, str), (
                "TypeError: Expecting pdf_files to be of type string."
            )
            self.pdf_file = pdf_file
        else:
            self.pdf_file = pdf_file

        if pages:
            assert self.pdf_file and not self.pdf_directory, (
                "Class parameter pages can only be used for single file conversions."
            )
            assert isinstance(pages, list) and all(isinstance(x, int) for x in pages), (
                "TypeError: Expecting pages to be list of integers."
            )
            self.pages = pages
        else:
            self.pages = pages

    @staticmethod
    def pdf_to_str(fname: str,
                   pages: list = None
                   ):
        """Convert PDF files to plain text.

        Arguments
        =========
        fname: str
            Full path to PDF file to convert.
        pages: list
            List of page page numbers in PDF file to convert

        Output
        ======
        text: str
            PDF text converted to a string.
        """

        # Get page numbers as a set
        if not pages:
            pagenums = set()
        else:
            pagenums = set(pages)

        # Set up PDF interpreter
        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(manager, output, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)

        # Open PDF file for reading
        infile = open(fname, 'rb')

        # Convert to string
        for page in PDFPage.get_pages(infile, pagenums):
            interpreter.process_page(page)
        infile.close()
        converter.close()
        text = output.getvalue()
        output.close
        return text

    def convert_multiple(self):
        # converts all pdfs in directory pdf_directory
        assert self.pdf_directory, (
            "ValueError: pdf_directory must be defined to run convert_multiple() method."
        )
        text_dict = dict()
        for pdf in os.listdir(self.pdf_directory):  # iterate through pdfs in pdf directory
            file_extension = pdf.split(".")[-1]
            if file_extension == "pdf":
                pdf_filename = self.pdf_directory + pdf
                text_dict[pdf_filename] = self.pdf_to_str(pdf_filename)
        return text_dict

    def convert_single(self):
        assert self.pdf_file, (
            "ValueError: pdf_file must be defined to run convert_single() method."
        )
        text = self.pdf_to_str(self.pdf_file, self.pages)
        return text
