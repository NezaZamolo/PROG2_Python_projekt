from fpdf import FPDF
import os

class PDFExporter:
    """
    A class to generate a PDF report for weather analysis.
    """
    def __init__(self, filename='weather_analysis.pdf'):
        """
        Initializes the PDFExporter with a given filename.
        :param filename:
        """
        self.pdf = FPDF()
        self.filename = filename
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def add_page_number(self):
        """
        Adds page number to the bottom of the page.
        :return:
        """
        self.pdf.set_y(-15)
        self.pdf.set_font("Helvetica", 'I', 8)
        self.pdf.cell(0, 10, f'Page {self.pdf.page_no()}', align='C')

    def add_title(self, title):
        """
        Adds a title to the PDF.
        :param title:
        :return:
        """
        self.pdf.add_page()
        self.pdf.set_font("Helvetica", 'B', 16)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.ln(10)

    def add_subheading(self, text):
        """
        Adds a subheading to the PDF.
        :param text:
        :return:
        """
        self.pdf.set_font("Helvetica", 'B', 12)
        self.pdf.cell(0, 10, text, ln=True)
        self.pdf.ln(2)

    def add_new_section(self, subtitle):
        """
        Adds a new section to the PDF with a subtitle.
        :param subtitle:
        :return:
        """
        self.pdf.add_page()
        self.pdf.set_font("Helvetica", 'B', 14)
        self.pdf.cell(0, 10, f"{subtitle} Overview", ln=True, align='C')
        self.pdf.ln(5)

    def add_text(self, text):
        """
        Adds a block of text to the PDF.
        :param text:
        :return:
        """
        self.pdf.set_font("Helvetica", size=12)
        self.pdf.multi_cell(0, 10, text)
        self.pdf.ln(3)

    def add_image_with_caption(self, image_path, caption, width=180):
        """
        Adds an image with a caption to the PDF.
        :param image_path:
        :param caption:
        :param width:
        :return:
        """
        if not os.path.exists(image_path):
            print(f"Image {image_path} does not exist.")
            return

        # Calculate the height based on the width and aspect ratio
        img_height = width * 9 / 16
        current_y = self.pdf.get_y()

        # Check if the image fits on the current page
        if current_y + img_height + 20 > self.pdf.h - self.pdf.b_margin:
            self.pdf.add_page()

        self.pdf.image(image_path, w=width)
        self.pdf.ln(2)
        self.pdf.set_font("Helvetica", 'I', 10)
        self.pdf.cell(0, 10, caption, ln=True, align='C')
        self.pdf.ln(5)

    def add_table(self, headers, rows):
        self.pdf.set_font("Helvetica", 'B', 12)

        # Calculate column widths based on the longest string in each column
        col_widths = []
        for i, header in enumerate(headers):
            max_width = self.pdf.get_string_width(header) + 6
            for row in rows:
                cell_width = self.pdf.get_string_width(str(row[i])) + 6
                max_width = max(max_width, cell_width)
            col_widths.append(max_width)

        # Adjust column widths to fit the page
        table_width = sum(col_widths)
        max_table_width = self.pdf.w - 2 * self.pdf.l_margin
        if table_width > max_table_width:
            scale = max_table_width / table_width
            col_widths = [w * scale for w in col_widths]

        row_height = 8
        x_start = self.pdf.get_x()
        y_start = self.pdf.get_y()

        # Header
        for i, header in enumerate(headers):
            self.pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
            self.pdf.multi_cell(col_widths[i], row_height, header, border=1, align='C')

        self.pdf.set_y(y_start + row_height)

        # Rows
        self.pdf.set_font("Helvetica", size=12)
        for row in rows:
            y_row_start = self.pdf.get_y()
            for i, item in enumerate(row):
                self.pdf.set_xy(x_start + sum(col_widths[:i]), y_row_start)
                self.pdf.multi_cell(col_widths[i], row_height, str(item), border=1, align='C')
            # Move down by one row height
            self.pdf.set_y(y_row_start + row_height)

        self.pdf.ln(5)

    def export(self):
        """
        Exports the PDF to a file.
        :return:
        """
        self.pdf.output(self.filename)
        print(f"PDF saved as {self.filename}")
