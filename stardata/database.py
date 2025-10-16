import csv
import glob
import json
import numpy as np
import pandas as pd
import sqlite3


def query(database, query, arguments = None):
# Runs a query on the SQLite database link provided
    # Get query type
    query_type = query.split()[0]
    
    try:
        with sqlite3.connect(database) as connection:
            # Create row factory and cursor
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            # Execute query
            cursor.execute(query, arguments)

            # If SELECT query, return results
            if query_type == "SELECT":
                rows = cursor.fetchall()
                if not rows:
                    return None
                return rows
            
            else: # For all other query types
                # Commit changes to database and return boolean confirmation
                connection.commit()
                return True
            
    except sqlite3.Error as err:
            # Return the error value to mark function failed
            return err


def upload_table(database, file_path, table_name):
# Uploads csv files from specified filepath to database as a table
    # Get datatypes from json file
    json_list = glob.glob(file_path + "/**.json", recursive = True)
    if len(json_list) == 1:
        with open(json_list[0], "r", encoding = "utf-8") as file:
            data_types = json.load(file)
    else:
        return "Unable to identify datatypes json file."

    col_headers = list(data_types.keys())

    # Get CSV file list
    csv_list = glob.glob(file_path + "/**.csv", recursive = True)

    # Extract data from csv file
    if len(csv_list) > 0:
        data_frames = []
        for file in csv_list:
            with open(file, newline = '') as csvfile:
                # Check for headers and read to dataframe
                if csv.Sniffer().has_header(csvfile.readline()):
                    data_frames.append(pd.read_csv(f"{file}", names = col_headers, header = 0, dtype = data_types))
                else:
                    data_frames.append(pd.read_csv(f"{file}", names = col_headers, dtype = data_types))
        table_data = pd.DataFrame(np.concatenate(data_frames), columns = col_headers)
    else:
        return ".csv files not found."

    # Set connection to SQLite database
    with sqlite3.connect(database) as connection:
        try:
            # Write to table using Pandas
            table_data.to_sql(table_name, connection)
        except ValueError:
            return f"{table_name} table already exists in stars.db."
    
    return True
