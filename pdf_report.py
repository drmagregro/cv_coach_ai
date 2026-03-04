import re
from fpdf import FPDF


def generate_pdf_report(original_text, analysis, doc_type, target_job):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_fill_color(102, 126, 234)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, f"Rapport Coach IA - {doc_type}", fill=True, ln=True, align="C")

    if target_job:
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Poste vise : {target_job}", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Document original", ln=True)
    pdf.set_draw_color(102, 126, 234)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    clean_original = original_text[:2000].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, clean_original)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Analyse et recommandations", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(60, 60, 60)
    clean_analysis = re.sub(r'[#*`]', '', analysis)
    clean_analysis = clean_analysis.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, clean_analysis)

    return bytes(pdf.output())