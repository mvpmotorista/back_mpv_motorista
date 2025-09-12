import camelot
import pandas as pd

# Extract all tables from page 1 of the PDF
tables = camelot.read_pdf('/home/hian/Downloads/MÁSCARA-PBEV-2025-JUL-29 (1).pdf', pages='all')

if tables:
    # Print the number of tables found
    print(f"Number of tables found: {len(tables)}")

    # Access the first table and convert it to a pandas DataFrame
    df = tables[0].df
    print(df)

    # Export all tables to a CSV file
    tables.export('output.csv', f='csv', compress=True)
else:
    print("No tables were found on the specified page.")
