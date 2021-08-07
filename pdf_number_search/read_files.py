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

    @staticmethod
    def pdf_to_str(fname: str,
                   pages: list = None
                   ):
        """Convert PDF file to plain text.

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

    def convert_multiple(self,
                         pdf_directory: str):
        """Convert all PDFs in directory pdf_directory.

        Arguments
        =========
        pdf_directory: str
            Directory containing PDF files to convert.

        Return
        ======
        text: str
            PDF text converted to a string.
        """
        # Check input
        assert isinstance(pdf_directory, str), (
            "Expecting pdf_directory to be of type string."
        )
        if pdf_directory[-1] != "/":
            pdf_directory = pdf_directory + "/"

        text_dict = dict()
        for pdf in os.listdir(pdf_directory):  # iterate through pdfs in pdf directory
            file_extension = pdf.split(".")[-1]
            if file_extension == "pdf":
                pdf_filename = pdf_directory + pdf
                text_dict[pdf_filename] = self.pdf_to_str(pdf_filename)
        return text_dict

    def convert_single(self,
                       pdf_file: str,
                       pages: list = None
                       ):
        """Convert single file

        Arguments
        =========
        pdf_file: str
            Full path to PDF file to convert.
        pages: list of integers
            Page numbers to convert.

        Return
        ======
        text: str
            PDF text converted to a string.
        """
        # Check input
        assert isinstance(pdf_file, str), (
            "Expecting pdf_files to be of type string."
        )
        if pages:
            assert isinstance(pages, list) and all(isinstance(x, int) for x in pages), (
                "Expecting pages to be list of integers."
            )

        # Convert PDF
        text = self.pdf_to_str(pdf_file, pages)
        return text
