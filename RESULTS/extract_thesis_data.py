import os
import re
import json

workspace_dir = r"c:\Users\Gaurav Singh\Downloads\MY THESIS WORK"
results_dir = os.path.join(workspace_dir, "RESULTS")
output_txt = os.path.join(results_dir, "extracted_thesis_data.txt")

extracted_content = []

# Try to find PDF libraries
pdf_lib = None
for lib in ['pypdf', 'fitz', 'PyPDF2', 'pdfminer']:
    try:
        __import__(lib)
        pdf_lib = lib
        break
    except ImportError:
        pass

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        return f"Error: File {pdf_path} not found"
    
    if pdf_lib == 'pypdf':
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text() or ""
        return text
    elif pdf_lib == 'fitz':
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            text += f"\n--- Page {i+1} ---\n"
            text += page.get_text()
        return text
    elif pdf_lib == 'PyPDF2':
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text() or ""
        return text
    else:
        # Fallback raw ascii extractor
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()
            matches = []
            for m in re.finditer(rb'\(([^)]+)\)', content):
                try:
                    s = m.group(1).decode('ascii', errors='ignore')
                    if len(s.strip()) > 1 and any(c.isalnum() for c in s):
                        matches.append(s)
                except:
                    pass
            return "\n".join(matches)
        except Exception as e:
            return f"Error reading PDF raw: {e}"

# 1. Extract text from Bhardwaj_2025_ApJ_989_130.pdf
bhardwaj_pdf = os.path.join(workspace_dir, "Bhardwaj_2025_ApJ_989_130.pdf")
print("Extracting Bhardwaj paper...")
bhardwaj_text = extract_text_from_pdf(bhardwaj_pdf)

# Search for values of interest in Bhardwaj paper text
bhardwaj_summary = []
lines = bhardwaj_text.split('\n')
for i, line in enumerate(lines):
    # Check if line contains parameter names
    if any(p in line.lower() for p in ['alpha', 'gamma', 'e_min', 'e_star', 'r_all_sky', 'sfr', 'stellar mass', 'mcmc', 'bayesian', 'contour', 'marginalized']):
        # Include context of 3 lines before and after
        start = max(0, i-2)
        end = min(len(lines), i+3)
        bhardwaj_summary.append(f"--- Context around line {i+1} ---")
        bhardwaj_summary.extend(lines[start:end])
        bhardwaj_summary.append("")

# 2. Extract text from all PDFs in RESULTS/contour_and_trace
print("Extracting results PDFs...")
results_pdf_text = []
contour_dir = os.path.join(results_dir, "contour_and_trace")
if os.path.exists(contour_dir):
    for f in os.listdir(contour_dir):
        if f.endswith('.pdf'):
            path = os.path.join(contour_dir, f)
            text = extract_text_from_pdf(path)
            results_pdf_text.append(f"=== PDF File: contour_and_trace/{f} ===")
            results_pdf_text.append(text)
            results_pdf_text.append("\n" + "="*40 + "\n")

# Write everything to the output file
with open(output_txt, 'w', encoding='utf-8') as f:
    f.write("=== BHARDWAJ PAPER TEXT SUMMARY ===\n")
    f.write("\n".join(bhardwaj_summary[:1000])) # limit summary to first 1000 lines of matches
    f.write("\n\n" + "="*80 + "\n\n")
    f.write("=== RESULTS PDFS TEXT ===\n")
    f.write("\n".join(results_pdf_text))

print(f"Done. Output saved to {output_txt}")
