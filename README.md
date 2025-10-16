# Stardata Project

# Table of Contents
- Overview
- Installation
- Usage
- Credits
- License

## Overview
This application calculates the distance between stars using data from the [AT-HYG stellar database](https://codeberg.org/astronexus/athyg.git). This was created for writers and game designers who want to implement realistic distances for interstellar travel. This project is intended for setup and use by an individual user.

While publically accessible distance calculators between stars exist, they usually require the stars to be named, or else require the user to input the coordinates of the stars directly. This calculator allows distance calculation between obscure stars, and can also list stars within a radius of another to create a "nearby stars" list.

The back end of the application uses an SQLite database and Python code to calculate distances, with a web-based front end to allow user interaction.

One of the objectives of this project was to avoid using the CS50 Python library. This opened up the opportunity to learn other modules and libraries in order to interface between python, SQL, and HTML.

### Back End
Python was used due to the large range of modules and frameworks available to support the interactions with databases, webpages, and mathematical calculations.

As SQLite has native support in Python, it was preferable to a server-based SQL implementation. A future improvement for this project would be to convert into using a more generic SQL approach such as SQLAlchemy. This would allow for a server-based database if that was the desired direction.

#### app.py
The main application file containing the core functions to take user input, retrieve information from the database, and calculate the response.

#### database.py
A support file containing functions to query the database and upload tables. This file is separated out as it has more generic uses in other projects.

#### starcalcs.py
A support file containing functions to perform calculations and sort information related to the star data. This file is specific to this project.

#### requirements.txt
An information file listing the python modules used in the project.

#### stars.db
An SQLite database containing the following tables:
- catalogue: stellar data from the [AT-HYG stellar database](https://codeberg.org/astronexus/athyg.git).
- habitable: stellar data from the [Habcat catalogue](https://www.projectrho.com/public_html/starmaps/supplement/APJ-HABCAT2.zip).
- notebook: stores user notes on specific stars.

### Front End
The Flask framework has been used to allow rendering of HTML pages via python script.

The front end is intended to provide a simple user interface for the application. A possible future improvement could be to create a stand-alone interface that is not web-based.

#### Appearance
- layout.html: The basic page layout that is extended using Flask to create full pages. It also contains the JavaScript code used by the pages to implement the radio buttons.
- styles.css: The style sheet.

#### Features
- index.html: The basic distance calculator. The user inputs two stars and clicks to calculate the distance in parsecs.
- stardata.html: The nearby stars calculator. The user inputs a star and radius to get a "sphere" of nearby stars.
- notebook.html: User can add notes to stars for later reference.
- load.html: User can load new databases into "catalogue" and "habitable" tables.
- error.html: Shows when an error occurs during operation.

# Installation
This application requires that python be installed along with the packages for flask, flask_session, numpy, and pandas. To set up this application on Windows, complete the following steps:
1. Download the "stardata" folder and move it to the desired location on your computer.
2. [Install python.](https://www.geeksforgeeks.org/python/how-to-install-python-on-windows/)
3. [Install pip.](https://www.geeksforgeeks.org/installation-guide/how-to-install-pip-on-windows/)
4. Use the command '''pip install ???''', substituting the package name for "???", to install flask, flask_session, numpy, and pandas.
5. Open the command prompt window.
6. Use the command '''cd /???''', substituting the folder location of the "stardata" folder for "???", to navigate to the folder.
7. Use the command '''python setup.py''' to generate the stars.db SQL database. A confirmation will appear in the command prompt window if successful.

# Usage
## How to Run
To use this application:
1. Open the command prompt window.
2. Use the command '''cd /???''', substituting the folder location of the "stardata" folder for "???", to navigate to the folder.
3. Use the command '''python app.py''' to run the application. This will open a browser window.
4. When done using the application, ensure you go back to the command prompt window and press "CTRL+C". You will see the file location reappear when successful.

## Database Selection
The [AT-HYG stellar database](https://codeberg.org/astronexus/athyg.git) is over 400MB when decompressed, which is too large to include as a single file on GitHub even when compressed. This project as supplied includes a smaller subset of the database.

This smaller subset can be replaced either with the full AT-HYG or any of the subsets that use the same schema, available under "data" at the link above.

To update the table data:
- Download the appropriate csv file.
- Replace the csv file in the stardata\table_data\catalogue or stardata\table_data\habitable folder with the new csv file.
- Navigate to the "Update Database" page.
- Select the option to update.

This should automatically drop the existing table and load the csv as a table in its place.

# Credits and Future Development
Thanks to David Nash for the [AT-HYG stellar database](https://codeberg.org/astronexus/athyg.git).

Future development paths for this project would make use of the additional stellar data to create more visualisations of stars and their locations. Creating a stand-alone file with a more custom interface would also be desirable. Refinement of the habitable world and planet data could be possible using the [Habitable Worlds Catalogue](https://phl.upr.edu/hwc/data).

# License
The [AT-HYG stellar database](https://codeberg.org/astronexus/athyg.git) is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).