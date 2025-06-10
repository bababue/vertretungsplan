import os
from flask import Flask, render_template, request, make_response
import psycopg2
import datetime
from markupsafe import escape

connection = psycopg2.connect(os.environ['DATABASE_URL'])

cursor = connection.cursor()

app = Flask(__name__)

def fetchSelectedEntries(date, kurs):
    if kurs == "Alle":
        query = """
        SELECT
            kurs AS Kurs,
            stunde AS Stunde,
            raum AS Raum,
            lehrer AS Lehrer,
            typ AS Typ,
            beschreibung as Beschreibung

        FROM vertretung
        WHERE datum = %s
        ORDER BY Kurs, Stunde;
        """
        cursor.execute(query, [date])
    else:
        query = """
        SELECT
            kurs AS Kurs,
            stunde AS Stunde,
            raum AS Raum,
            lehrer AS Lehrer,
            typ AS Typ,
            beschreibung as Beschreibung

        FROM vertretung
        WHERE datum = %s
        AND kurs IN (%s)
        ORDER BY Kurs, Stunde;
        """
        cursor.execute(query, [date, kurs])

    return cursor.fetchall()

def fetchCourses():
    query = """
            SELECT DISTINCT kurs FROM vertretung
            ORDER BY kurs;
            """
    cursor.execute(query)
    return(cursor.fetchall())


@app.route("/", methods=["GET"])
def index():
    cookie_course = request.cookies.get("last_course")
    default_course = "Alle" if cookie_course == None else cookie_course #Set the default course to "Alle" or, if exists, the current cookie value

    current_date = datetime.date.today().strftime("%Y-%m-%d")

    return render_template(
        "index.html",
        default_date=current_date,
        default_course=default_course,
        courses=fetchCourses()
    )


@app.route("/query", methods=["POST"])
def query():
    # Load both date and course from the post dat
    selected_date = escape(request.form["date"])
    selected_course = escape(request.form["kurs"])

    results = fetchSelectedEntries(selected_date, selected_course)

    alle_selected = True if selected_course == "Alle" else False

    resp = make_response(
        render_template("results.html", results=results, alle_selected=alle_selected)
    )
    resp.set_cookie("last_course", value = selected_course, expires=datetime.datetime.now() + datetime.timedelta(days=365))
    return resp
