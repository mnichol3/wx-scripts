#!/bin/python
"""
Python 3.6

Write a text file to PDF.

11 AUG 2020
"""
from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):

    def __init__(self):
        """
        Create a new instance of a PDF object and set the following attributes:
        * Format : letter
        * Right margin : 15
        * Left margin  : 15
        * Top margin   : 15
        * Font : Courier 12
        """
        super(PDF, self).__init__(format='letter')
        self.set_right_margin(15)
        self.set_left_margin(15)
        self.set_top_margin(10)
        self.set_font('Courier', '', 12)

    def add_product(self, text):
        """
        Add a product to the PDF, which will start on a new page.

        Parameters
        ----------
        text : str
            Text to write to the PDF.

        Returns
        -------
        None.
        """
        self.add_page()
        self.alias_nb_pages()
        self.write_text(text)

    def write_text(self, text):
        """
        Write text to the PDF in the form of a multi-cell.

        Parameters
        ----------
        text : str
            Text to write to the PDF.

        Returns
        -------
        None.
        """
        self.set_font('Courier', '', 12)
        self.multi_cell(w=0, h=5, txt=text, align='L')

    def save(self, filename):
        """
        Write the PDF object to a PDF file.

        Parameters
        ----------
        filename : str
            Name of the PDF file.

        Returns
        -------
        None.
        """
        self.output(filename)

    def header(self):
        dt_stamp = self._get_datetime()
        self.set_font('Courier', '', 12)
        self.cell(130)
        self.cell(30, 10, dt_stamp, 0, 0, 'L')
        self.ln(10)

    def footer(self):
        """
        Construct the page footer.
        Function is automatically called by add_page().
        """
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Courier', '', 10)
        # Page number
        self.cell(0, 10, str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def _reset_font(self):
        self.set_font('Courier', '', 12)

    def _get_datetime(self):
        """
        Get the datetime string used in the header.

        Parameters
        ----------
        None.

        Returns
        -------
        str : Current date & time.
            Format: DoW DDMonYYYY HH:MMz
        """
        now = datetime.utcnow()
        prefix = now.strftime('%a %d')      # Day of week & day of month
        suffix = now.strftime('%Y %H:%Mz')  # Year and UTC time
        month  = now.strftime('%b').upper() # Month caste to upper-case
        dt = '{}{}{}'.format(prefix, month, suffix)
        return dt



# Read saved TWDAT for testing
f = '../tests/twdat-20200728_1745.txt'
with open(f, 'r') as fopen:
    content = fopen.read()

pdf = PDF()
pdf.add_product(content)
pdf.add_product(content)
pdf.save("mygfg.pdf")
