import json
import os
import webbrowser

from database import query, upload_table
from flask import Flask, render_template, request
"""from flask_session import Session"""
from starcalcs import calculate_distance, create_star, get_nearby, select_id, update_position

# Configure application
app = Flask(__name__)
"""
# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
"""

# Set database location
db = os.path.dirname(os.path.abspath(__file__)) + r"\stars.db"

# Get catalogue information
file_path = os.path.dirname(os.path.abspath(__file__)) + r"\\catalogues.json"
if os.path.isfile(file_path):
    with open(file_path, "r", encoding = "utf-8") as file:
        catalogues = json.load(file)
else:
    raise SystemExit("catalogues.json not found.")

# Create star lists for each catalogue
star_lists = {}
for key, value in catalogues.items():
    rows = query(db, value["list_query"], ())
    # Convert result to list of strings
    row_list = []
    for row in rows:
        row_list.append(dict(row))
    star_list = [str(x) for x in list(map(lambda d: d.get(key, "-"), row_list))]
    star_lists[key] = star_list

# Define routes
@app.route("/", methods = ["GET", "POST"])
def index():
# Show form to select two stars
    if request.method == "POST":
    # Return page with selected star data
        # Get IDs and catalogues for requested stars
        try:
            inputs = [(request.form.get("starA"), request.form.get("catA")), 
                    (request.form.get("starB"), request.form.get("catB"))
                    ]
        except:
            return render_template("error.html", error = "Inputs not found.")

        try:
            epoch = int(request.form.get("year"))
        except:
            epoch = 2000

        # Create star objects
        stars = []
        try:
            for input in inputs:
                stars.append(create_star(input, catalogues, db))
        except:
            return render_template("error.html", error = "Unable to create star object.")
        
        # Calculate positions for provided year
        xyz = []
        for star in stars:
            xyz.append(update_position(star.xyz, epoch))

        # Calculate distance between stars
        distance = calculate_distance(xyz)
 
        # Return page with star data
        result = f"The distance between {stars[0].ref} and {stars[1].ref} in {epoch} is {distance: .3f} parsecs."
        return render_template("index.html", catalogues = catalogues, datalists = star_lists, message = result, starL = stars[0].__dict__, starR = stars[1].__dict__)
    
    else: # request method == "GET"
    # Return page without star data
        return render_template("index.html", catalogues = catalogues, datalists = star_lists, message = "", starL = "", starR = "")
    

@app.route("/stardata", methods = ["GET", "POST"])
def stardata():
# Show form to get data on a single star
    if request.method == "POST":
    # Return page with star data
        # Get ID and catalogue for requested star
        try:
            input = (request.form.get("star"), 
                    request.form.get("cat"), 
                    int(request.form.get("range")))
        except:
            return render_template("error.html", error = "Inputs not found.")
    
        # Create star object
        try:
            star = create_star(input, catalogues, db)
        except:
            return render_template("error.html", error = "Unable to create star object.")
                
        # Get list of stars in range
        nearby_list = get_nearby(star, input[2], db)        
        
        # Return page with star data
        result = f"Stars within {input[2]} parsecs of {star.ref}"
        return render_template("stardata.html", catalogues = catalogues, datalists = star_lists, message = result, nearby = nearby_list, star = star.__dict__)
    
    else: # request method == "GET"
    # Return page without star data
        instruction = "Select catalogue and star to see data and nearby systems."
        return render_template("stardata.html", catalogues = catalogues, datalists = star_lists, message = instruction, nearby = "", star = "")


@app.route("/notebook", methods = ["GET", "POST"])
def notebook():
# Update user notes on a specific star
    if request.method == "POST":
        # Get star id and related information
        try:
            input = (int(request.form.get('star_id')), request.form.get("starnotes"))
        except:
            return render_template("error.html", error = "Inputs not found.")

        # Create star object
        try:
            star = create_star((input[0], "id"), catalogues, db)
        except:
            return render_template("error.html", error = "Unable to create star object.")
        star.ref = select_id(star.ids)

        # If no changes were made
        if input[1] == star.notes:
            return render_template("stardata.html", message = f"No changes to notebook for {star.ref}.", catalogues = catalogues, datalists = star_lists, star = star, nearby = "")
    
        # Otherwise update notes for star
        note_lookup = query(db, "SELECT * FROM notebook WHERE catalogue_id = ?;", (star.ids["id"],))
        if note_lookup == None:
            result = query(db, "INSERT INTO notebook (notes, catalogue_id) VALUES (?, ?);", (input[1], star.ids["id"]))
        else:
            note_id = int(note_lookup[0]["id"])
            result = query(db, "UPDATE notebook SET notes = ? WHERE id = ?;", (input[1], note_id))
        star.notes = input[1]

        # Redirect to correct page
        if result == True:
            return render_template("stardata.html", catalogues = catalogues, datalists = star_lists, message = f"Notebook updated for {star.ref}.", nearby = "", star = star)
        else:
            return render_template("error.html", error = f"Unable to update notebook table for {star.ref}.")
    
    else: # request method == "GET"
        # Get star id and related information
        star_id = int(request.args.get('star_id'))
        
        # Create star object
        star = create_star((star_id, "id"), catalogues, db)
        star.ref = select_id(star.ids)

        # Render page
        return render_template("notebook.html", star = star.__dict__)


@app.route("/load", methods = ["GET", "POST"])
def load():
# Update the catalogue and habitable tables in the database
    if request.method == "POST":
        # Determine which button was pressed
        try:
            table_name = request.form.get("table_name")
        except:
            return render_template("error.html", error = "Could not retrieve table name.")

        if table_name != "catalogue" and table_name != "habitable":
            return render_template("error.html", f"Invalid table name {table_name} supplied.")

        # Get file path
        file_path = os.path.dirname(os.path.abspath(__file__)) + r"\table_data\\" + table_name

        # Drop existing table
        if table_name == "catalogue":
            result = query(db, "DROP TABLE IF EXISTS catalogue;", ())
        elif table_name == "habitable":
            result = query(db, "DROP TABLE IF EXISTS habitable;", ())
        if result != True: # if the transaction failed
            return render_template("error.html", error = f"Drop table query for {table_name} returned error: {result}")

        # Upload new table
        result = upload_table(db, file_path, table_name)
        if result != True:
            return render_template("error.html", error = f"Could not upload {table_name} table: {result}")

        # Render page
        report = f"{table_name} table updated."
        return render_template("load.html", message = report)
    
    else: # request method == "GET"
        # Render page
        prompt = "Select table to update."
        return render_template("load.html", message = prompt)


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run()