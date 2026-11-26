"""Extract key financial data from WALMEX 2023 annual report PDF."""
import pdfplumber
import sys

PDF = "D:/Temp/walmex_2023.pdf"
with pdfplumber.open(PDF) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    # Extract specific pages of interest
    for label, pages in [
        ("DEBT_TABLES", range(120, 170)),
    ]:
        print(f"\n========== {label} ==========")
        for i in pages:
            if i < len(pdf.pages):
                t = pdf.pages[i].extract_text() or ""
                # only print pages with relevant keywords
                if any(k in t.lower() for k in ["préstamo", "crédito", "bono", "emisión", "vencimiento", "tasa de interés", "deuda total", "pasivo total", "liquidez"]):
                    print(f"\n--- PAGE {i+1} ---")
                    print(t[:3000])
                    print()
