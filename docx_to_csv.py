import csv
import docx
import sys
import os

def convert_docx_to_rag_csv(docx_path, csv_path):
    if not os.path.exists(docx_path):
        print(f"Error: File not found at {docx_path}")
        sys.exit(1)

    try:
        doc = docx.Document(docx_path)
    except Exception as e:
        print(f"Error opening docx: {e}")
        sys.exit(1)

    rows = []
    current_headings = []
    
    # Iterate over paragraphs
    # We will try to maintain a context stack of headings
    
    chunk_id = 0
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name.lower()
        
        # Check if it's a heading
        if 'heading' in style_name:
            try:
                level = int(style_name.replace('heading', '').strip())
                # Update current headings stack
                # If level is 1, clear everything. If level is 2, keep level 1, etc.
                # Actually, standard logic: keep headings with level < current level
                
                # Adjust list size
                if level <= len(current_headings):
                    current_headings = current_headings[:level-1]
                
                current_headings.append(text)
                
            except ValueError:
                # Assuming non-standard heading style name, just treat as text or context?
                # For now let's treat it as context if it looks like a title
                 pass
        else:
            # It's content
            # Combine current headings into a context string
            context = " > ".join(current_headings)
            
            rows.append({
                'id': chunk_id,
                'source': os.path.basename(docx_path),
                'context': context,
                'text': text
            })
            chunk_id += 1

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'source', 'context', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Successfully converted {len(rows)} chunks to {csv_path}")

if __name__ == "__main__":
    docx_file = "ISSS Website Breakdown.docx"
    csv_file = "rag_data.csv"
    convert_docx_to_rag_csv(docx_file, csv_file)
