import sqlite3

from flask import Flask
from flask import render_template
from flask import request

from PrintMetrics import *

app = Flask(__name__)
app.debug = True

# Helpers functions
def prepare_table(results):
    title = ["Project"]
    for column in columns: 
        title.append(column)
    data = []
    for project in results.keys():
        result = results[project]["metrics"]
        result["name"] = project
        data.append(result)
    print(data)
    return [title, data]

def prepare_artifacts_table(results):
    title = ["Artifact"]
    for column in columns_detail: 
        title.append(column)
    data = []
    for project in results.keys():
        for artifact in results[project]["detail"]:
            result = results[project]["detail"][artifact]["metrics"]
            result["name"] = artifact
            data.append(result)
    return [title, data]




@app.route("/")
def landing():
    return render_template('landing.html', projects=artifacts.keys())

@app.route("/project")
def project():
    detail = {}
    project_name = request.args.get('project_name')
    if project_name.startswith('"'):
        project_name = project_name[1:-1]
    
    conn = get_db_connection()
    projects = conn.execute(f'SELECT * FROM projects where project_name="{project_name}" order by id').fetchall()
    conn.close()
    column_names = ["Project", "Created"]
    for column in columns: 
        column_names.append(column)
    column_artifact_names = ["Artifact", "Created"]
    for column in columns_detail: 
        column_artifact_names.append(column)
    return render_template('project_metrics.html', results=projects, column_names=column_names)


@app.route("/detail")
def detail():
    project_run_id = request.args.get('project_run_id')
    conn = get_db_connection()
    projects = conn.execute(f'SELECT * FROM projects where id = {project_run_id}').fetchall()
    artifacts = conn.execute(f'SELECT * FROM artifacts where project_run_id = {project_run_id}').fetchall()
    conn.close()
    column_project_names = ["Project", "Created"]
    column_artifact_names = ["Artifact", "Created"]
    for column in columns_detail: 
        column_artifact_names.append(column)
    for column in columns:
        column_project_names.append(column)
    return render_template('project_detail_metrics.html', results=projects, artifacts=artifacts, column_names=column_project_names, column_artifact_names=column_artifact_names)
