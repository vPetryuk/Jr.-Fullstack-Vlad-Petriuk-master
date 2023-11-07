import csv
import uuid
from io import StringIO
from django.core.files.base import ContentFile
from .models import CsvFile  # Replace with the actual import for your CsvFile model


def create_enriched_csv_file(original_csv_file_instance, enriched_csv_data):
    # Step 1: Gather all unique keys (column names) from all rows
    all_keys = set()
    for row in enriched_csv_data:
        all_keys.update(row.keys())
    all_keys = list(all_keys)  # Convert to list to maintain consistent order

    # Step 2: Generate the CSV content with all keys
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=all_keys)
    writer.writeheader()
    for row in enriched_csv_data:
        writer.writerow(row)

    # Step 3: Generate a new filename
    new_filename = f"{original_csv_file_instance.name}_Enriched_{uuid.uuid4()}.csv"

    # Step 4: Create a new CsvFile instance and save the CSV content to a file
    new_csv_file = CsvFile()
    new_csv_file.name = new_filename
    new_csv_file.csv_file.save(new_filename, ContentFile(csv_buffer.getvalue()))
    new_csv_file.save()

    return new_csv_file
