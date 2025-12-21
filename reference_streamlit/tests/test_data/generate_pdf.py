from fpdf import FPDF


def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, text="This is a test PDF file.",
             new_x='LMARGIN', new_y='NEXT', align="C")
    pdf.output("C:/Users/malle/Resume  Screening/tests/test_data/test.pdf")


if __name__ == "__main__":
    create_pdf()
