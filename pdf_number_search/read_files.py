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

import pdf_number_search.utils as utils


class PDFNumberFinder(object):

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

        Return
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
        """Convert all PDFs in directory pdf_directory to strings.

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

        # Iterate through pdfs in pdf directory and convert to plain text
        text_dict = dict()
        for pdf in os.listdir(pdf_directory):
            file_extension = pdf.split(".")[-1]
            if file_extension == "pdf":
                pdf_filename = pdf_directory + pdf
                # Save to dictionary
                text_dict[pdf_filename] = self.pdf_to_str(pdf_filename)
        return text_dict

    def convert_single(self,
                       pdf_file: str,
                       pages: list = None
                       ):
        """Convert single file to string.

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

    @staticmethod
    def text2int(textnum,
                 numwords=None):
        """Convert alpha number to numerals.

        The function takes a number spelled out in english and converts it
        to a numeric number.
            e.g. "five hundred and twenty one" ==> 521

        Arguments
        =========
        textnum: str
            Number written out in English
        numwords: dict
            Dictionary of number words and their multiplier for converting to numerals

        Return
        ======
        result: float
            Converted number in numerals
        """
        if not numwords:
            # Set numwords dictionary
            numwords["and"] = (1, 0)
            for idx, word in enumerate(utils.units):
                numwords[word] = (1, idx)
            for idx, word in enumerate(utils.tens):
                numwords[word] = (1, idx * 10)
            for idx, word in enumerate(utils.scales):
                numwords[word] = (10 ** (idx * 3 or 2), 0)

        # Convert english number to numerals
        current = 0
        result = 0
        for word in textnum.split():
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        result = float(result + current)
        return result

    @staticmethod
    def split_sentences(text):
        """Split string into a list of strings where each element is a sentence.

        Arguments
        =========
        text: str
            Text to be split into a list of strings

        Return
        ======
        split_text: list
            List of sentences.
        """
        split_text = text.split(".")
        split_text = [s for s in split_text if len(s) != 0]
        split_text = [s.replace("\n", " ") for s in split_text]
        return split_text

    def translate_number_sentences(self,
                                   split_text: list):
        """Search list of sentences for mentions of numbers. Convert all numbers from
        alpha characters to numerals.

        Arguments
        =========
        split_text: list of strings
            List of sentences to search for numbers

        Return
        ======
        translated_str: list of strings
            List of sentences with all numbers converted to numerals.
        """
        # Check input
        assert isinstance(split_text, list) and all(isinstance(x, int) for x in split_text), (
            "Expecting split_text to be list of strings."
        )

        translated_str = list()
        for sent_num, statement in enumerate(split_text):  # enumerate(test_text_list):
            s = statement.lower()

            # remove commas from numbers
            match = re.findall(r"(,\d{3})", s)
            for m in match:
                replacement = re.sub(r",", "", m)
                s = s.replace(m, replacement)

            # separate non number characters from numbers by space
            s = re.sub(r"([0-9]+(\.[0-9]+)?)", r" \1 ", s).strip()

            word_split = s.split(" ")

            # Remove empty strings
            word_split = [w for w in word_split if w != ""]

            # Does sentence contain integers or number words
            if any(substring in word_split for substring in utils.number_words) | bool(re.search(r'\d', s)):
                word_i = list()
                used_num_words = list()
                for idx, word in enumerate(word_split):

                    # If numbers have commas, remove them
                    if re.search(r'\d', word):
                        num_no_commas = float(word.replace(",", ""))
                        word_as_list = [word]
                        j = 1

                        # check if there are number words after the number
                        if idx + j < len(word_split):
                            while word_split[idx + j] in utils.number_words:
                                try:
                                    num_no_commas = num_no_commas * utils.num_scale[word_split[idx + j]]
                                    word_as_list.append(word_split[idx + j])
                                    used_num_words.append(word_split[idx + j])
                                    j += 1
                                except Exception as e:
                                    print(e)
                                    print("Problem sentence:")
                                    print(f"    {s}")
                                    j += 1

                                # break out of while loop if at end of sentence
                                if (idx + j) == len(word_split):
                                    break

                        # sub in float for number words
                        word_split[idx: idx + j] = [str(num_no_commas)]
                        # rebuild sentence
                        s = " ".join(word_split)

                    # Get indices of number words not already translated
                    if word in used_num_words:
                        used_num_words.remove(word)
                    elif word in utils.number_words:
                        word_i.append(idx)

                # Check if there are any number words left to translate
                if len(word_i) > 0:
                    all_word_nums_i = list()
                    # there is a non number word in between number words
                    if (word_i[-1] - word_i[0]) != (len(word_i) - 1):

                        # Split indices into lists of consecutive indices
                        consec_indices = list()
                        for k, g in groupby(enumerate(word_i), lambda i_x: i_x[0] - i_x[1]):
                            consec_indices.append(list(map(itemgetter(1), g)))

                        # combine lists of indices if they only skip one number
                        # and the word corresponding to the missing index is "and"
                        for i, l in enumerate(consec_indices[:-1]):
                            if l[0] in [el for consec in all_word_nums_i for el in consec]:
                                continue
                            elif (consec_indices[i + 1][0] - l[-1] == 2) & (word_split[l[-1] + 1] == "and"):
                                all_word_nums_i.append(l + [l[-1] + 1] + consec_indices[i + 1])
                            else:
                                all_word_nums_i.append(l)

                        if consec_indices[-1][0] not in [el for consec in all_word_nums_i for el in consec]:
                            all_word_nums_i.append(consec_indices[-1])

                    else:
                        # There is only one number with no non-number words within
                        all_word_nums_i = [word_i]

                    # take each word list and translate it to an integer
                    for word_i in all_word_nums_i:
                        full_number = " ".join([word_split[i] for i in word_i])
                        numeric_sub = self.text2int(full_number)

                        if len(word_split) > word_i[-1] + 1:
                            word_split[word_i[0]: word_i[-1] + 1] = [str(numeric_sub)] + [""] * (len(word_i) - 1)
                        else:
                            word_split[word_i[0]:] = [str(numeric_sub)]

                    s = " ".join([w for w in word_split if w != ""])

                translated_str.append(s)
        return translated_str
