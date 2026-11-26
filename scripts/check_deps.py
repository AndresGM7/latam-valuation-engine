import sys
try:
    import reportlab
    print(f"reportlab {reportlab.Version}")
except Exception as e:
    print("reportlab NOT INSTALLED:", e)
try:
    import PyPDF2
    print(f"PyPDF2 {PyPDF2.__version__}")
except Exception as e:
    print("PyPDF2 NOT INSTALLED:", e)
try:
    import pdfplumber
    print(f"pdfplumber {pdfplumber.__version__}")
except Exception as e:
    print("pdfplumber NOT INSTALLED:", e)
