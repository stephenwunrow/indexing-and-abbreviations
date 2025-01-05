from docx import Document
import re
from tqdm import tqdm
from lxml import etree
import zipfile

def read_docx(file_path):
    """Read the content of a Word document and extract abbreviations from the 'LIST OF ABBREVIATIONS' section."""
    doc = Document(file_path)
    abbreviations = []
    manuscript_lines = []
    
    # Step 1: Identify 'LIST OF ABBREVIATIONS' and 'CHAPTER 1'
    list_started = False
    chapter_started = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:  # Ignore empty paragraphs
            if text.upper() == "LIST OF ABBREVIATIONS":
                list_started = True
                continue  # Skip adding "LIST OF ABBREVIATIONS" itself
            
            if text.upper() == "CHAPTER 1":
                chapter_started = True
                continue  # Skip adding "CHAPTER 1" itself

            if list_started and not chapter_started:
                # Extract the abbreviation before the tab
                match = re.match(r'^([^\t]+)\t', text)
                if match:
                    abbreviations.append(match.group(1).strip())

            if chapter_started:
                # Add to manuscript section
                manuscript_lines.append(text)

    return abbreviations, manuscript_lines

def get_footnotes(docx_file):
    """Extract footnotes from the Word document using XML parsing."""
    footnotes = []

    # Open the DOCX file as a zip archive
    with zipfile.ZipFile(docx_file, 'r') as docx_zip:
        # Check if footnotes.xml exists in the archive
        if 'word/footnotes.xml' in docx_zip.namelist():
            footnote_xml = docx_zip.read('word/footnotes.xml')
            footnote_tree = etree.fromstring(footnote_xml)

            # Extract footnote text
            for footnote in footnote_tree.xpath('//w:footnote', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                texts = [node.text for node in footnote.xpath('.//w:t', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})]
                # Join the texts to form the complete footnote
                footnotes.append(''.join(texts))

    # Join all footnotes into a single string for easier searching
    return ' '.join(footnotes)

def search_in_doc(element, manuscript_lines, footnotes_text):
    """Search for an abbreviation in the manuscript and footnotes (ignoring punctuation/whitespace)."""
    element = re.escape(element)  # Escape special characters in the abbreviation for safe regex search
    pattern = r'\b' + element + r'\b'  # Ensure the abbreviation is a standalone word
    
    # Search in manuscript lines
    found_in_text = any(re.search(pattern, line) for line in manuscript_lines)
    
    # Search in footnotes
    found_in_footnotes = re.search(pattern, footnotes_text) is not None
    
    return found_in_text or found_in_footnotes

def main(source_file):
    # Step 1: Read and split lines from the Word file
    abbreviations, manuscript_lines = read_docx(source_file)
    
    # Step 2: Extract footnotes
    footnotes_text = get_footnotes(source_file)  # Reuse the footnote extraction function
    
    # Step 3: Filter abbreviations that are not found in the manuscript section or footnotes
    not_found_abbreviations = []
    
    # Use tqdm to create a progress bar
    for element in tqdm(abbreviations, desc="Processing abbreviations", unit="abbr"):
        if element:  # Ignore empty lines
            stripped_element = element.strip('. “”‘’,')
            found = search_in_doc(stripped_element, manuscript_lines, footnotes_text)
            
            # If not found, add to the list of not found abbreviations
            if not found:
                not_found_abbreviations.append(element)
                print(f"Not found: {stripped_element}")
    
    # Step 4: Print the list of abbreviations not found
    if not_found_abbreviations:
        print("Abbreviations not found:")
        for abbr in not_found_abbreviations:
            print(abbr)
    else:
        print("All abbreviations were found.")

# Example usage
source_file = 'Dissertation.docx'  # The Word file containing abbreviations and manuscript

main(source_file)
