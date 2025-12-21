from fpdf import FPDF
from docx import Document
import os


def generate_pdf_report(result, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Resume Analysis Report", 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(
        0, 10, f"Overall Score: {result.get('resume_score', 'N/A')}/100", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Summary", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, result.get('ai_summary', 'Not available.'))
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Matching Skills", 0, 1)
    pdf.set_font("Arial", '', 12)
    for skill in result.get('matching_skills', []):
        pdf.cell(0, 10, f"- {skill}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Missing Skills", 0, 1)
    pdf.set_font("Arial", '', 12)
    for skill in result.get('missing_skills', []):
        pdf.cell(0, 10, f"- {skill}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Improvement Suggestions", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, result.get(
        'improvement_suggestions', 'Not available.'))

    pdf.output(file_path)


def generate_docx_report(result, file_path):
    doc = Document()
    doc.add_heading('Resume Analysis Report', level=1)
    doc.add_heading(
        f"Overall Score: {result.get('resume_score', 'N/A')}/100", level=2)

    doc.add_heading('Summary', level=3)
    doc.add_paragraph(result.get('ai_summary', 'Not available.'))

    doc.add_heading('Matching Skills', level=3)
    for skill in result.get('matching_skills', []):
        doc.add_paragraph(skill, style='List Bullet')

    doc.add_heading('Missing Skills', level=3)
    for skill in result.get('missing_skills', []):
        doc.add_paragraph(skill, style='List Bullet')

    doc.add_heading('Improvement Suggestions', level=3)
    doc.add_paragraph(result.get('improvement_suggestions', 'Not available.'))

    doc.save(file_path)


def generate_resume_pdf(data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, data['full_name'], 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(
        0, 5, f"{data['email']} | {data['phone']} | {data['linkedin']}", 0, 1, 'C')
    pdf.ln(5)

    # Summary
    if data['summary']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Professional Summary", 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, data['summary'])
        pdf.ln(5)

    # Education
    if data['education_school']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Education", 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 5, data['education_school'], 0, 1)
        pdf.set_font("Arial", '', 11)
        pdf.cell(
            0, 5, f"{data['education_degree']} - {data['education_year']}", 0, 1)
        pdf.ln(5)

    # Experience
    if data['job_title']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Experience", 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 5, f"{data['job_title']} at {data['company']}", 0, 1)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, data['job_description'])
        pdf.ln(5)

    # Skills
    if data['skills']:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Skills", 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, data['skills'])

    pdf.output(file_path)
