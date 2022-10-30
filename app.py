import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///courses.db")

#global variable points per grade for different unit types
e90 = {'D': 24, 'M': 15, 'P': 9, 'N': 6, 'U': 0}
e120 = {'D': 32, 'M': 20, 'P': 12, 'N': 8, 'U': 0}
i60 = {'D': 16, 'M': 10, 'P': 6, 'U': 0}
i90 = {'D': 24, 'M': 15, 'P': 9, 'U': 0}
i120 = {'D': 32, 'M': 20, 'P': 12, 'U': 0}

#global variable grade thresholds for different courses
stream_thresholds = {'extcert': {'D*': 90, 'D': 74, 'M': 52, 'P': 36, 'U': 0}, 'dip': {'D*D*': 180, 'D*D': 162, 'DD': 144, 'DM': 124, 'MM': 104, 'MP': 88, 'PP': 72, 'U': 0}, 'extdip': {'D*D*D*': 270, 'D*D*D': 252, 'D*DD': 234, 'DDD': 216, 'DDM': 196, 'DMM': 176, 'MMM': 156, 'MMP': 140, 'MPP': 124, 'PPP': 108, 'U': 0}}

def get_unitlist():
    courses = db.execute('SELECT * FROM COURSES')
    unitlist = {}

    for course in courses:
        courseid = course['course_id']
        coursename = course['name']

        units = db.execute('SELECT title FROM UNITS WHERE course_id = ?', courseid)
        ulist = []
        for unit in units:
            ulist.append(unit['title'])
        unitlist[coursename] = ulist

    return unitlist

def calculate_points(selected_course, selected_units):

    points = 0

    for (unit, grade) in selected_units.items():
        if ((db.execute("SELECT type FROM UNITS WHERE title = ?", unit)[0]['type']) == 'External'):
            if ((db.execute("SELECT glh FROM UNITS WHERE title = ?", unit)[0]['glh']) == '120'):
                points += e120[grade]
            else:
                points += e90[grade]
        elif ((db.execute("SELECT type FROM UNITS WHERE title = ?", unit)[0]['type']) == 'Internal'):
            if ((db.execute("SELECT glh FROM UNITS WHERE title = ?", unit)[0]['glh']) == '120'):
                points += i120[grade]
            elif ((db.execute("SELECT glh FROM UNITS WHERE title = ?", unit)[0]['glh']) == '90'):
                points += i90[grade]
            else:
                points += i60[grade]

    return points


@app.route("/extcert")
def extcert():
    """
    initialize drop down menus
    """
    unitlist = get_unitlist()

    default_courses = sorted(unitlist.keys())

    return render_template('extcert.html',
                       all_courses=default_courses,)

@app.route("/dip")
def dip():
    """
    initialize drop down menus
    """
    unitlist = get_unitlist()

    default_courses = sorted(unitlist.keys())

    return render_template('dip.html',
                       all_courses=default_courses,)

@app.route("/extdip")
def extdip():
    """
    initialize drop down menus
    """
    unitlist = get_unitlist()

    default_courses = sorted(unitlist.keys())

    return render_template('extdip.html',
                       all_courses=default_courses,)


@app.route('/_update_dropdown')
def update_dropdown():

    unitlist = get_unitlist()

    selected_course = request.args.get('selected_course', type=str)

    updated_values = unitlist[selected_course]

    html_string_selected = ''
    for entry in updated_values:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/_calculate_grade')
def calculate_extcert_grade():

    selected_course = request.args.get('selected_course', type=str)
    points_ref = request.args.get('points_ref', type=str)

    selected_units = {}
    for i in range(1, int(len(request.args)/2)):
        selected_units[request.args.get(str(f'unit{i}'))] = request.args.get(str(f"grade{i}"))

    total_points = calculate_points(selected_course, selected_units)

    for (stream, thresholds) in stream_thresholds.items():
        if stream == points_ref:
            for i, (grade, threshold_points) in enumerate(thresholds.items()):
                if total_points >= threshold_points:
                    final_grade = grade
                    break

    return jsonify(grade_report="Your total points are: {}. Your estimated grade is: {}".format(total_points, final_grade))