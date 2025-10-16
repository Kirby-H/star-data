import os

from database import query, upload_table
from pathlib import Path

# Set database location
this_directory = os.path.dirname(os.path.abspath(__file__))
db_name = r"\stars.db"
db = this_directory + db_name

if Path(db).is_file():
    print(f"SQL database {db_name} already exists.")
else:
    # Get file paths
    file_paths = {
        "catalogue": this_directory + r"\table_data\\catalogue",
        "habitable": this_directory + r"\table_data\\habitable"
        }

    # Create new tables
    for key, value in file_paths.items():
        result = upload_table(db, value, key)
        if result != True:
            print(f"Could not upload {key} table: {result}")

    # Add notebook table
    notebook_create = """
        CREATE TABLE notebook (
        id INTEGER NOT NULL PRIMARY KEY,
        catalogue_id INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY (catalogue_id) REFERENCES catalogue (id)
        );
        """
    result = query(db, notebook_create, ())
    if result != True:
        print(f"Could not create notebook table: {result}")

    print(f"SQL database {db_name} successfully created.")