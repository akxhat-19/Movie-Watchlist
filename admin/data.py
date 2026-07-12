from flask import Blueprint,render_template
from app import db,Users,Movies
data = Blueprint("data" , __name__ , static_folder = "static" , template_folder = "templates")

@data.route("/view")
def view():
    users = Users.query.all()
    return render_template("database.html" , users=users)

if(__name__ == '__main__'):
    data.run(debug=True)
