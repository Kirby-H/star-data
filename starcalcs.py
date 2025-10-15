from database import query
from decimal import Decimal as d

class Star:
    def __init__(self, ref, ids, pos, xyz, magspec, habitable, notes):
        self.ref = ref
        self.ids = ids
        self.pos = pos
        self.xyz = xyz
        self.magspec = magspec
        self.habitable = habitable
        self.notes = notes


def calculate_distance(xyz):
# Calculate distance between the two supplied cartesian positions
    # Check that two positions were supplied
    if len(xyz) != 2:
        print(len(xyz))
        return None
    
    # Get cartesian coordinates of the positions
    x = (xyz[0]["x0"], xyz[1]["x0"])
    y = (xyz[0]["y0"], xyz[1]["y0"])
    z = (xyz[0]["z0"], xyz[1]["z0"])

    # Calculate and return distance between them
    distance = (
        (d(x[0]) - d(x[1]))**2 + 
        (d(y[0]) - d(y[1]))**2 + 
        (d(z[0]) - d(z[1]))**2
        ).sqrt()
    return distance
    

def create_star(request, catalogues, db):
# Returns a Star object for the provided information

    # Get correct database query for catalogue
    data_query = ""
    for key, value in catalogues.items():
        print(key)
        if key == request[1]:
            data_query = value["data_query"]
            append_cat = value["append_cat"]
            # Split columns into (flam, bayer, con) for Bayer Flamsteed Combined
            if key == "bf":
                args = request[0].split()
            else:
                args = (request[0],)
            break
    
    # Set reference name
    if append_cat == True:
        ref = f"{request[1]}: {request[0]}"
    else:
        ref = request[0]

    # Run database query to get star AT-HYG ID
    if data_query == "":
        star_rows = None
    else:
        star_rows = query(db, data_query, args)[0]
    
    # Convert star_data to dictionary and split into sections
    star_dict = dict(star_rows)

    ids_list = ["id", "tyc", "gaia", "hyg", "hip", "hd", "hr", "gl", "bayer", "flam", "con", "proper"]
    ids = {key: star_dict[key] for key in ids_list}
    
    pos_list = ["ra", "dec", "pos_src", "dist", "rv", "rv_src", "pm_ra", "pm_dec", "pm_src"]
    pos = {key: star_dict[key] for key in pos_list}

    xyz_list = ["x0", "y0", "z0", "dist_src", "vx", "vy", "vz"]
    xyz = {key: star_dict[key] for key in xyz_list}

    magspec_list = ["mag", "absmag", "ci", "mag_src", "spect", "spect_src"]
    magspec = {key: star_dict[key] for key in magspec_list}

    # Get notes and habitable status
    if star_dict["proper"] == "Sol" or query(db, "SELECT * FROM habitable WHERE HIP = ?", (star_dict["hip"],)) != None:
        habitable = True
    else:
        habitable = False

    try:    
        notes = dict(query(db, "SELECT notes FROM notebook WHERE catalogue_id = ?", (star_dict["id"],))[0])["notes"]
    except:
        notes = None
    
    # Create and returns Star object
    star = Star(ref, ids, pos, xyz, magspec, habitable, notes)
    return star


def get_nearby(star, radius, db):
# Returns a list of stars within the given radius of the requested star
    # Calculate max and min coordinates for a "box" around the origin star
    x_max = star.xyz["x0"] + radius
    x_min = star.xyz["x0"] - radius
    y_max = star.xyz["y0"] + radius
    y_min = star.xyz["y0"] - radius
    z_max = star.xyz["z0"] + radius
    z_min = star.xyz["z0"] - radius  

    # Query database for list of stars
    nearby_box = query(db, 
                 "SELECT * FROM catalogue WHERE (x0 BETWEEN ? AND ?) AND (y0 BETWEEN ? AND ?) AND (z0 BETWEEN ? AND ?);", 
                 (x_min, x_max, y_min, y_max, z_min, z_max))

    # Calculate actual distances and assemble list to return
    nearby_list = []
    for candidate in nearby_box:
        # Eliminate the origin star itself from the results
        if candidate["id"] != star.ids["id"]:
            # Calculate the distance and only include stars actually within the radius
            distance = calculate_distance([star.xyz, candidate])
            if distance <= radius:
                # Select user-facing ID to use for star and add tuple to list
                cand_ref = select_id(candidate)
                nearby_list.append((cand_ref, distance, candidate["id"]))
    
    # Sort list by distance from origin and return it
    nearby_list.sort(key=lambda x: x[1])
    return nearby_list


def select_id(ids):
# Selects an ID from a dictionary of IDs to use as a reference.
    if ids["proper"] != None:
        prefer_id = ids["proper"]
    elif ids["gl"] != None:
        prefer_id = ids["gl"]
    elif ids["flam"] != None and ids["bayer"] != None and ids["con"] != None:
        prefer_id = f"{ids["flam"]} {ids["bayer"]} {ids["con"]}"
    elif ids["tyc"] != None:
        prefer_id = f"tyc: {ids["tyc"]}"
    elif ids["hyg"] != None:
        prefer_id = f"hyg: {ids["hyg"]}"
    elif ids["hr"] != None:
        prefer_id = f"hr: {ids["hr"]}"
    elif ids["hip"] != None:
        prefer_id = f"hip: {ids["hip"]}"
    elif ids["hd"] != None:
        prefer_id = f"hd: {ids["hd"]}"
    elif ids["gaia"] != None:
        prefer_id = f"gaia: {ids["gaia"]}"
    else:
        prefer_id = f"athyg: {ids["id"]}"
    
    return prefer_id


def update_position(xyz, epoch):
# Update stellar coordinates for provided year, based on cartesian coordinates for J2000.0 epoch in parsecs
    # Yearly cartesian motion in km/s
    motion = {key: xyz[key] for key in ["vx", "vy", "vz"]}
    # Difference in years between J2000.0 epoch and supplied year
    years = d(epoch - 2000)

    # Update motion values
    for key in motion:
        if motion[key] == None:
            motion[key] = 0
        # Multiply by difference in epoch
        motion[key] = d(motion[key]) * years
        # Convert km/s to pc/year
        motion[key] = motion[key] * d(1.02271128e-6)
    
    # Update and return position
    xyz["x0"] = d(xyz["x0"]) + motion["vx"]
    xyz["y0"] = d(xyz["y0"]) + motion["vy"]
    xyz["z0"] = d(xyz["z0"]) + motion["vz"]
    return xyz


"""
# Unused functions - require "import math" as written.

def calculate_distance(stars):
# Calculate distance between the two supplied stars in parsecs
    # Check that two stars were supplied
    if len(stars) != 2:
        print(len(stars))
        return None

    # Get spherical coordinates of the stars
    s_coords = to_coords(stars)
    r = [s_coords[0]["r"], s_coords[1]["r"]]
    phi = [s_coords[0]["phi"], s_coords[1]["phi"]]
    theta = [s_coords[0]["theta"], s_coords[1]["theta"]]

    # Calculate and return distance between them
    distance = math.sqrt(
        r[0]**2 + r[1]**2 - 2*r[0]*r[1]*(
            math.sin(phi[0])*
            math.sin(phi[1])*
            math.cos(theta[0]-theta[1]) + (math.cos(phi[0])*math.cos(phi[1]))
            )
        )
    return distance

def to_coords(stars):
# Converts equatorial coordinates (dist, ra, dec) to spherical (r, phi, theta)
    spherical = []
    for star in stars:
        # radial distance from Earth in parsecs
        r = star.pos["dist"]

        # polar angle (angle from polar axis to distance vector) from declination
        phi = math.radians((star.pos["dec"] - 90)*(-1))

        # azimuthal angle (angle around polar axis to distance vector) from right ascension
        theta = math.radians(star.pos["ra"] * 15)

        # add coordinates to list as a dictionary
        spherical.append({"r": r, "phi": phi, "theta": theta})
    return spherical


def to_cartesian(coords):
# Converts spherical coordinates (r, phi, theta) to cartesian (x, y, z)
    cartesian = []
    for position in coords:
        p = position["r"] * math.sin(position["phi"])
        x = p * math.cos(position["theta"])
        y = p * math.sin(position["theta"])
        z = position["r"] * math.cos(position["phi"])
        cartesian.append({"x": x, "y": y, "z": z})
    return cartesian

def to_spherical(coords):
# Converts cartesian coordinates (x, y, z) to spherical (r, phi, theta)
    spherical = []
    for position in coords:
        r = math.sqrt(position["x"]**2 + position["y"]**2 + position["z"]**2)
        phi = math.acos(position["z"] / r)
        theta = math.atan(position["y"] / position["x"])
        spherical.append({"r": r, "phi": phi, "theta": theta})
    return spherical
"""
    