import re
import zipfile
from docx import Document
from xml.etree import ElementTree as ET

# Function to wrap italicized text with %...%%
def wrap_italic_in_percent(runs):
    wrapped_text = ""
    for run in runs:
        if run.italic:
            wrapped_text += f'%{run.text}%%' if run.text else ''
        else:
            wrapped_text += run.text if run.text else ''
    return wrapped_text

# Function to revert %...%% sections back to italics
def revert_percent_to_italics(runs):
    for run in runs:
        if run.text and '%' in run.text:
            run.text = re.sub(r'%(.+?)%%', r'\1', run.text)

# Function to ignore text wrapped in smart quotes or %...%%
def ignore_wrapped_text(text):
    return re.sub(r'“.+?”|%.*?%%', '', text)

# Function to replace abbreviations in text
def replace_abbreviations_in_text(text, abbrev_dict):
    modified_text = text
    for old, new in abbrev_dict.items():
        pattern = rf'(\b{old}\b)( \d+)'
        modified_text = re.sub(pattern, rf'{new}\2', modified_text)
    return modified_text

# Function to process paragraphs and replace abbreviations
def process_paragraphs(doc, abbrev_dict):
    for paragraph in doc.paragraphs:
        # Wrap italicized text temporarily
        wrapped_text = wrap_italic_in_percent(paragraph.runs)
        safe_text = ignore_wrapped_text(wrapped_text)

        # Replace abbreviations in the paragraph text
        modified = False
        for old, new in abbrev_dict.items():
            pattern = rf'(\b{old}\b)( \d+)'
            if re.search(pattern, safe_text):
                # Update paragraph text with modified text
                paragraph.text = re.sub(pattern, rf'{new}\2', paragraph.text)
                modified = True

        if modified:
            revert_percent_to_italics(paragraph.runs)

# Main processing function
def process_document(input_file, output_file, abbrev_dict):
    doc = Document(input_file)

    # Process paragraphs to replace abbreviations
    process_paragraphs(doc, abbrev_dict)

    # Save the document after processing paragraphs
    doc.save(output_file)

# Abbreviation replacements
abbrev_dict = {
    "Matt": "Mt.",
    "Mark": "Mk",
    "Luke": "Lk.",
    "John": "Jn",
    "Acts": "Acts",
    "Rom": "Rom.",
    "1 Cor": "1 Cor.",
    "2 Cor": "2 Cor.",
    "Gal": "Gal.",
    "Eph": "Eph.",
    "Phil": "Phil.",
    "Col": "Col.",
    "1 Thess": "1 Thess.",
    "2 Thess": "2 Thess.",
    "1 Tim": "1 Tim.",
    "2 Tim": "2 Tim.",
    "Tit": "Tit.",
    "Philem": "Phlm.",
    "Heb": "Heb.",
    "James": "Jas",
    "1 Pet": "1 Pet.",
    "2 Pet": "2 Pet.",
    "1 John": "1 Jn",
    "2 John": "2 Jn",
    "3 John": "3 Jn",
    "Jude": "Jude",
    "Rev": "Rev.",
    "Pss Sol": "Pss. Sol.",
    "Gen": "Gen.",
    "Exod": "Exod.",
    "Lev": "Lev.",
    "Num": "Num.",
    "Deut": "Deut.",
    "Josh": "Josh.",
    "Judg": "Judg.",
    "1 Sam": "1 Sam.",
    "2 Sam": "2 Sam.",
    "1 Chron": "1 Chron.",
    "2 Chron.": "2 Chron.",
    "Neh": "Neh.",
    "Ps": "Ps.",
    "Pss": "Pss.",
    "Prov": "Prov.",
    "Isa": "Isa.",
    "Jer": "Jer.",
    "Lam": "Lam.",
    "Ezek": "Ezek.",
    "Dan": "Dan.",
    "Hos": "Hos.",
    "Obad": "Obad.",
    "Jon": "Jon.",
    "Mic": "Mic.",
    "Nah": "Nah.",
    "Hab": "Hab.",
    "Zeph": "Zeph.",
    "Hag": "Hag.",
    "Zech": "Zech.",
    "Mal": "Mal."
}

# Run the processing and save to a new file
process_document("Dissertation.docx", "New_Dissertation.docx", abbrev_dict)
