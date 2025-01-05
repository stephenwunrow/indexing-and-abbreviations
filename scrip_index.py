import pdfplumber
import re

### NOTES:
# Need to deal with verse only references in lists
# Need to figure out how to identify the correct book name, particularly in Revelation with "John"
# Need to organize and create final output

# Define the list of books and their abbreviations
books = {
    # Pseudepigrapha (common texts)
    "1 Enoch": ["1 Enoch", "1 En"],
    "2 Enoch": ["2 Enoch", "2 En"],
    "Jubilees": ["Jub"],
    "3 Maccabees": ["3 Macc", "3 Ma"],
    "4 Maccabees": ["4 Macc", "4 Ma"],
    "2 Baruch": ["2 Bar"],
    "4 Ezra": ["4 Ezra"],
    "Epistle of Barnabas": ["Barn"],
    "Testaments of the Twelve Patriarchs": ["T12P", "T12 Pat"],
    "Ascension of Isaiah": ["Ascen. Isa."],

    # Old Testament
    "Genesis": ["Gen"],
    "Exodus": ["Exod", "Ex"],
    "Leviticus": ["Lev"],
    "Numbers": ["Num"],
    "Deuteronomy": ["Deut", "Deu"],
    "Joshua": ["Josh", "Jos"],
    "Judges": ["Judg", "Jdg"],
    "Ruth": ["Ruth", "Ru"],
    "1 Samuel": ["1 Sam", "1 Sa"],
    "2 Samuel": ["2 Sam", "2 Sa"],
    "1 Kings": ["1 Kgs", "1 Ki"],
    "2 Kings": ["2 Kgs", "2 Ki"],
    "1 Chronicles": ["1 Chr", "1 Ch"],
    "2 Chronicles": ["2 Chr", "2 Ch"],
    "Ezra": ["Ezra", "Ezr"],
    "Nehemiah": ["Neh"],
    "Esther": ["Est"],
    "Job": ["Job"],
    "Psalms": ["Ps", "Pss"],
    "Proverbs": ["Prov", "Pr"],
    "Ecclesiastes": ["Eccl", "Ecc"],
    "Song of Solomon": ["Song", "Sg"],
    "Isaiah": ["Isa", "Is"],
    "Jeremiah": ["Jer"],
    "Lamentations": ["Lam"],
    "Ezekiel": ["Ezek", "Eze"],
    "Daniel": ["Dan", "Da"],
    "Hosea": ["Hos"],
    "Joel": ["Joel"],
    "Amos": ["Amos"],
    "Obadiah": ["Obad", "Ob"],
    "Jonah": ["Jonah", "Jon"],
    "Micah": ["Mic"],
    "Nahum": ["Nah"],
    "Habakkuk": ["Hab"],
    "Zephaniah": ["Zeph", "Zep"],
    "Haggai": ["Hag"],
    "Zechariah": ["Zech", "Zec"],
    "Malachi": ["Mal"],
    
    # New Testament
    "Matthew": ["Matt", "Mt"],
    "Mark": ["Mk"],
    "Luke": ["Lk"],
    "John": ["Jn"],
    "Acts": ["Acts"],
    "Romans": ["Rom", "Ro"],
    "1 Corinthians": ["1 Cor", "1 Co"],
    "2 Corinthians": ["2 Cor", "2 Co"],
    "Galatians": ["Gal"],
    "Ephesians": ["Eph"],
    "Philippians": ["Phil"],
    "Colossians": ["Col"],
    "1 Thessalonians": ["1 Thess", "1 Th"],
    "2 Thessalonians": ["2 Thess", "2 Th"],
    "1 Timothy": ["1 Tim", "1 Ti"],
    "2 Timothy": ["2 Tim", "2 Ti"],
    "Titus": ["Tit"],
    "Philemon": ["Phlm", "Phm"],
    "Hebrews": ["Heb"],
    "James": ["Jas"],
    "1 Peter": ["1 Pet", "1 Pe"],
    "2 Peter": ["2 Pet", "2 Pe"],
    "1 John": ["1 Jn"],
    "2 John": ["2 Jn"],
    "3 John": ["3 Jn"],
    "Jude": ["Jude"],
    "Revelation": ["Rev"],
    
    # Apocryphal Books (Deuterocanonical)
    "Tobit": ["Tob"],
    "Judith": ["Jdt"],
    "Additions to Esther": ["Add Esth", "Add Est"],
    "Wisdom": ["Wis"],
    "Sirach": ["Sir", "Ecclesiasticus"],
    "Baruch": ["Bar"],
    "Letter of Jeremiah": ["Ep Jer"],
    "Prayer of Azariah": ["Pr Az"],
    "Susanna": ["Sus"],
    "Bel and the Dragon": ["Bel"],
    "1 Maccabees": ["1 Macc", "1 Ma"],
    "2 Maccabees": ["2 Macc", "2 Ma"],
    "1 Esdras": ["1 Esd"],
    "2 Esdras": ["2 Esd"],
    "Prayer of Manasseh": ["Pr Man"],
    "Psalm 151": ["Ps 151"],
}

# A regex pattern for detecting book names (full or abbreviated forms)
book_pattern = re.compile(r'\b(' + '|'.join([re.escape(book) for book in books.keys()] + 
                                            [re.escape(abbr) for abbr_list in books.values() for abbr in abbr_list]) + r')\b')

# A regex pattern for detecting verse references (e.g., 1:1, 3:16)
verse_pattern = re.compile(r'\b\d+:\d+[–, \d]*\b')

# Function to map any abbreviation or full name match to the full book title
def get_full_book_name(match):
    # Check if the match is a full name
    if match in books:
        return match
    # If it's an abbreviation, find the corresponding full title
    for full_name, abbreviations in books.items():
        if match in abbreviations:
            return full_name
    return None  # Return None if no match is found

# Initialize the current book reference to persist across pages
current_book = None

# Open the PDF file
with pdfplumber.open("test.pdf") as pdf:
    verse_references = []

    # Loop through each page of the PDF
    for i, page in enumerate(pdf.pages):
        implicit_page_number = i - 25  # Keep track of the implicit page number
        
        # Extract text from the page
        text = page.extract_text()
        
        # Find all book references and verse references in the text
        book_matches = list(book_pattern.finditer(text))
        verse_matches = list(verse_pattern.finditer(text))

        # Keep a list of book matches to track the closest book before each verse
        book_positions = []

        for match in book_matches:
            full_book_name = get_full_book_name(match.group(0))
            book_positions.append((match.start(), full_book_name))
        
        # For each verse, find the closest preceding book reference and handle multiple verses
        for verse_match in verse_matches:
            verse_text = verse_match.group(0)  # Get the matched verse reference
            chapter, verses = verse_text.split(':')  # Split into chapter and verse part
            individual_verses = verses.split(',')    # Split verses by comma

            # Find the closest preceding book reference
            verse_position = verse_match.start()
            for book_position, book_name in reversed(book_positions):
                if book_position < verse_position:
                    current_book = book_name
                    break

            # Append each individual verse reference
            for verse in individual_verses:
                verse_references.append({
                    "verse": f"{chapter}:{verse.strip()}",
                    "page": implicit_page_number,
                    "book": current_book
                })

# Output the list of verse references with page numbers and book titles
for ref in verse_references:
    print(f"Book: {ref['book']}, Verse: {ref['verse']}, Page: {ref['page']}")
