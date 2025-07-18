# Moon Highlighter - Python Version

A Python CLI application that processes PDF book highlights based on data stored in an SQLite database.

## Features

- Searches for highlights of a specific book in an SQLite database
- Locates text in the PDF and identifies approximate coordinates
- Automatic mapping of database colors to RGB colors
- Generates detailed processing report
- Saves a new PDF with processed information
- Test version for quick validation

## Prerequisites

- Python 3.7 or higher
- SQLite3 (usually included with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JuninhoFreitas/moonreader-export-pdf-with-highlights
cd moon-highlighter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version
```bash
python moon_highlighter.py --gui
```

### DEPRECATED!!!
#### Complete Version
```bash
python moon_highlighter.py -p <pdf_path> -b <book_name> -d <database_path> [-o <output_path>]
```

#### Test Version (Recommended)
```bash
python moon_highlighter_simple.py -p <pdf_path> -b <book_name> -d <database_path> [-o <output_path>] [-l <limit>]
```

### Test Script
```bash
python test_highlighter.py
```

### Parameters

- `-p, --pdf`: Path to the PDF file to be processed
- `-b, --book`: Book name (must exactly match the name in the SQLite database)
- `-d, --database`: Path to the SQLite database
- `-o, --output`: (Optional) Output PDF path
- `-l, --limit`: (Simple version only) Number of highlights to process (default: 10)

### Usage Example

```bash
# Initial test
python test_highlighter.py

# Test version with 5 highlights
python moon_highlighter_simple.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite" -l 5

# Complete version
python moon_highlighter.py -p "CONTEXTUALIZAÇÃO Missionária.pdf" -b "CONTEXTUALIZAÇÃO Missionária.pdf" -d "pdfmarks.sqlite"
```

## How It Works

1. **Database Reading**: The application connects to the SQLite database and executes the query:
   ```sql
   SELECT highlightColor, highlightLength, original 
   FROM notes 
   WHERE book = ? AND bookmark = ''
   ```

2. **Color Mapping**: Each color value from the database is mapped to a hexadecimal color:
   - 1996532479 → #FFFF00 (Yellow)
   - -1996554240 → #00FF00 (Green)
   - 2013265664 → #0000FF (Blue)
   - -256 → #FF0000 (Red)
   - 16711680 → #FF00FF (Pink)

3. **Text Search**: For each highlight, the text is searched in the PDF using PyPDF2

4. **Coordinate Identification**: Approximate coordinates are calculated based on text position

5. **Saving**: A new PDF is saved with the processed information

## Database Structure

The application expects a `notes` table with the following structure:

```sql
CREATE TABLE notes (
    _id integer primary key autoincrement,
    book text,
    filename text,
    lowerFilename text,
    lastChapter NUMERIC,
    lastSplitIndex NUMERIC,
    lastPosition NUMERIC,
    highlightLength NUMERIC,
    highlightColor NUMERIC,
    time NUMERIC,
    bookmark text,
    notetext text,
    original text,
    underline NUMERIC,
    strikethrough NUMERIC,
    bak text
);
```

## Generated Files

1. **Output PDF**: Copy of the original processed PDF
   - Complete version: `{original_name}_highlighted.pdf`
   - Test version: `{original_name}_test_highlighted.pdf`
   - Can be customized with the `-o` parameter

## Processing Report

The application displays a detailed report during and after processing:

```
Processing 5 test highlights for book: CONTEXTUALIZAÇÃO Missionária.pdf
Found 5 highlights for testing
Processing highlight 1/5: um desafio à igreja de Cristo...
  ✗ Not found in PDF
Processing highlight 2/5: A ideia textual, portanto...
  ✗ Not found in PDF
Processing highlight 3/5: A Palavra é supracultural...
  ✗ Not found in PDF
Processing highlight 4/5: Contextualizar o evangelho...
  ✗ Not found in PDF
Processing highlight 5/5: Apresentar Cristo é a finalidade...
  ✓ Found (1 occurrences) - Color: #0000FF

=== TEST REPORT ===
Total processed: 5
Found: 1
Not found: 4
Success rate: 20.0%
```

## Limitations and Considerations

- **Search Accuracy**: Text search is exact. Small formatting differences may prevent location
- **Visual Highlights**: PyPDF2 has limitations for adding visual highlights. The application identifies text but does not add visual markings
- **Approximate Coordinates**: Coordinates are calculated approximately based on text position
- **Performance**: For very large PDFs or with many highlights, processing may be slow

## Customization

### Color Mapping

To customize color mapping, edit the `map_color` method in the class:

```python
def map_color(self, color_value: int) -> str:
    color_map = {
        1996532479: "#FFFF00",    # Yellow
        -1996554240: "#00FF00",   # Green
        # Add more colors as needed
    }
    # ... rest of the code
```

## Error Handling

- Validation of required parameters
- File existence verification
- Database error handling
- PDF manipulation error handling
- Fallback to default colors in case of error

## Dependencies

- **PyPDF2**: Library for PDF manipulation
  - Version: 3.0.1
  - License: BSD (free)

## Comparison with Go Version

| Feature | Python | Go |
|---|---|---|
| **Text Identification** | ✅ Implemented | ⚠️ Basic |
| **PDF Manipulation** | ✅ Complete | ⚠️ Basic |
| **Visual Highlights** | ❌ Limited | ❌ Not implemented |
| **Performance** | ⚠️ Moderate | ✅ Fast |
| **Ease of Use** | ✅ Simple | ⚠️ Moderate |
| **Dependencies** | ✅ Minimal | ⚠️ Multiple |
| **Success Rate** | ⚠️ ~20% | ❓ Not tested |

## Application Files

- `moon_highlighter.py`: Complete version of the application
- `moon_highlighter_simple.py`: Simplified version for testing
- `test_highlighter.py`: Test script to validate data
- `requirements.txt`: Python dependencies
- `README_Python.md`: This documentation

## License

This project is open source and can be used freely. 