# importing flask
from flask import *
import pymysql
import pymysql.cursors
import os

# initialize app
app = Flask(__name__)

from flask_cors import CORS
CORS(app)

# configure upload folder
app.config["UPLOAD_FOLDER"] = 'static/images'


# =========================
# SIGNUP API
# =========================
@app.route("/api/signup", methods=["POST"])
def signup():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    phone = request.form["phone"]
    role = request.form.get("role", "buyer")

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor()

    sql = "INSERT INTO users(username,email,password,phone,role) VALUES(%s,%s,%s,%s,%s)"

    data = (username, email, password, phone, role)

    cursor.execute(sql, data)
    connection.commit()

    return jsonify({"message": "User registered successfully"})


# =========================
# SIGNIN API
# =========================
@app.route("/api/signin", methods=["POST"])
def signin():

    email = request.form["email"]
    password = request.form["password"]

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM users WHERE email=%s AND password=%s"

    data = (email, password)

    cursor.execute(sql, data)

    if cursor.rowcount == 0:
        return jsonify({"message": "login failed"})
    else:
        user = cursor.fetchone()
        return jsonify({"message": "login successful", "user": user})


# =========================
# ADD PROPERTY API
# =========================
@app.route("/api/addproperty", methods=["POST"])
def addproperty():

    title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    city = request.form["city"]
    area = request.form["area"]
    pincode = request.form["pincode"]
    property_type = request.form["propertyType"]
    bhk = request.form["bhk"]
    bathrooms = request.form["bathrooms"]
    area_size = request.form["areaSize"]
    furnishing = request.form["furnishing"]
    seller_id = request.form["seller_id"]

    images = request.files.getlist("images")

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor()

    sql = """
    INSERT INTO properties
    (title,description,price,city,area,pincode,property_type,bhk,bathrooms,area_size,furnishing,seller_id)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    data = (title, description, price, city, area, pincode,
            property_type, bhk, bathrooms, area_size, furnishing, seller_id)

    cursor.execute(sql, data)
    connection.commit()

    property_id = cursor.lastrowid

    # save images
    for img in images:
        filename = img.filename
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        img.save(path)

        cursor.execute(
            "INSERT INTO property_images(property_id,image_url) VALUES(%s,%s)",
            (property_id, filename)
        )

    connection.commit()

    return jsonify({"message": "Property uploaded successfully"})


# =========================
# GET PROPERTIES API
# =========================
@app.route("/api/properties")
def getproperties():

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM properties WHERE status='sale'")

    properties = cursor.fetchall()

    return jsonify(properties)


# =========================
# VERIFY PROPERTY
# =========================
@app.route("/api/admin/verify", methods=["POST"])
def verify():

    property_id = request.form["property_id"]

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor()

    sql = "UPDATE properties SET is_verified=TRUE WHERE id=%s"

    cursor.execute(sql, (property_id,))
    connection.commit()

    return jsonify({"message": "Property verified"})


# =========================
# ADMIN USERS
# =========================
@app.route("/api/admin/users")
def users():

    email = request.args.get("email")

    connection = pymysql.connect(
        user="root",
        host="localhost",
        password="",
        database="realestate_plan"
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND role='admin'",
        (email,)
    )

    admin = cursor.fetchone()

    if not admin:
        return jsonify({"message": "Access denied"})

    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()

    return jsonify(all_users)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)