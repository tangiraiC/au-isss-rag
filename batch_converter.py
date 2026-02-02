import csv
import docx
import sys
import os
import glob
from pypdf import PdfReader

def extract_from_docx(docx_path):
    chunks = []
    try:
        doc = docx.Document(docx_path)
    except Exception as e:
        print(f"Error opening docx {docx_path}: {e}")
        return []

    current_headings = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name.lower()
        
        if 'heading' in style_name:
            try:
                level = int(style_name.replace('heading', '').strip())
                if level <= len(current_headings):
                    current_headings = current_headings[:level-1]
                current_headings.append(text)
            except ValueError:
                 pass
        else:
            context = " > ".join(current_headings)
            chunks.append({
                'source': os.path.basename(docx_path),
                'context': context,
                'text': text
            })
    return chunks

def extract_from_pdf(pdf_path):
    chunks = []
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error opening pdf {pdf_path}: {e}")
        return []

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text:
                chunks.append({
                    'source': os.path.basename(pdf_path),
                    'context': f"Page {i+1}",
                    'text': text.strip()
                })
        except Exception as e:
            print(f"Error reading page {i} of {pdf_path}: {e}")

    return chunks

def batch_convert(directory, csv_path):
    all_chunks = []
    
    # Process DOCX
    for filepath in glob.glob(os.path.join(directory, "*.docx")):
        print(f"Processing {filepath}...")
        all_chunks.extend(extract_from_docx(filepath))

    # Process PDF
    for filepath in glob.glob(os.path.join(directory, "*.pdf")):
        print(f"Processing {filepath}...")
        all_chunks.extend(extract_from_pdf(filepath))

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'source', 'context', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, chunk in enumerate(all_chunks):
            chunk['id'] = i
            writer.writerow(chunk)

    print(f"Successfully converted {len(all_chunks)} chunks from {len(glob.glob(os.path.join(directory, '*.docx')))+len(glob.glob(os.path.join(directory, '*.pdf')))} files to {csv_path}")

if __name__ == "__main__":
    directory = "raw_documents"
    csv_file = "processed_data/rag_data.csv"
    batch_convert(directory, csv_file)
