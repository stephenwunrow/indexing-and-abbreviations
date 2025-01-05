from docx import Document
import re
import zipfile
from lxml import etree

### NOTE: probably need to start with bibliography, store all the data, and then create the citations from that. 

def read_docx(file_path):
    """Read the content of a Word document and return footnotes."""
    footnotes = []
    with zipfile.ZipFile(file_path, 'r') as docx_zip:
        if 'word/footnotes.xml' in docx_zip.namelist():
            footnote_xml = docx_zip.read('word/footnotes.xml')
            footnote_tree = etree.fromstring(footnote_xml)
            for footnote in footnote_tree.xpath('//w:footnote', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                footnote_text = []
                for paragraph in footnote.xpath('.//w:p', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                    for run in paragraph.xpath('.//w:r', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                        text = run.xpath('.//w:t/text()', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                        if text:
                            run_text = ''.join(text)
                            # Check for italics and wrap italic text in quotes
                            if run.xpath('.//w:rPr/w:i', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
                                run_text = f'"{run_text}"'  # Wrap italic text in double quotes
                            footnote_text.append(run_text)

                footnotes.append(''.join(footnote_text))
    print(footnotes)
    
    return footnotes

def find_short_citations(footnotes):
    """Find short citations following the pattern 'Capitalized word(s), quoted or italicized phrase'."""
    short_citations = []
    short_citation_pattern = re.compile(r'([A-Z][a-zA-Z]+), (["“][^"“”]+["”]|‘[^‘’]+’)')  # Regex pattern for short citations
    
    for footnote in footnotes:
        matches = short_citation_pattern.findall(footnote)
        if matches:
            for match in matches:
                citation = f'{match[0]}, {match[1]}'
                short_citations.append(citation.strip())
    
    return list(set(short_citations))  # Remove duplicates

def find_long_citation(short_citation, footnotes):
    """Find the long citation in the footnotes using the capitalized part of the short citation."""
    # Extract the capitalized word(s) and the quoted phrase from the short citation
    match = re.match(r'([A-Z][a-zA-Z]+), [“‘]([^“”‘’]+)[’”]', short_citation)
    if not match:
        return None
    
    capitalized_part = re.escape(match.group(1))
    phrase_part = match.group(2).strip(',. ')

    # Search for the capitalized part followed by the phrase part in the footnotes
    long_citation_pattern = re.compile(rf'({capitalized_part}, [“‘"][^"“‘’”]*{phrase_part}[^"“‘’”]*[’”"])')
    for footnote in footnotes:
        long_match = long_citation_pattern.search(footnote)
        if long_match:
            return long_match.group(1).strip()
    
    return None

def main(file_path):
    # Step 1: Read footnotes
    footnotes = read_docx(file_path)

    # Step 2: Find short citations in the footnotes
    short_citations = find_short_citations(footnotes)

    # Step 3: Build a dictionary of short citations and corresponding long citations
    citation_dict = {}
    
    for short_citation in short_citations:
        long_citation = find_long_citation(short_citation, footnotes)
        if long_citation:
            citation_dict[short_citation] = long_citation
        else:
            citation_dict[short_citation] = "Long citation not found"

    # Step 4: Print the dictionary of short to long citations
    print("Citation Dictionary:")
    for short_citation, long_citation in citation_dict.items():
        print(f"{short_citation} -> {long_citation}")

# Example usage
source_file = 'Dissertation.docx'  # The Word file containing footnotes
main(source_file)
