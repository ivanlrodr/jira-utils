import sys
import sqlite3

from GitHub import *
from JiraMetrics import *
from Sonar import *

### Information about projects
artifacts = {'TM' : {'bat-testgmana' : 'inditexcodingfashion_TMBATCH', 'lib-samplemgmt': 'inditexcodingfashion_SAMPLEMGMT', 'mic-tmblockintegration': 'inditexcodingfashion_TMBLOCKINT', 'wsc-seguridadsaludproducto': 'inditexcodingfashion_SSPSWREST', 'wsc-testingmanagementservicios': 'inditexcodingfashion_TMSWREST', 'wsc-testingmanagementlaboratoriosultimate': 'inditexcodingfashion_TMSWREST'},#, 'web-testingmanagement' : 'inditexcodingfashion_CPSIA', 'lib-testingmanagementgwt' : 'inditexcodingfashion_TMLIBGWT', 'lib-testingmanagementcomun' : 'inditexcodingfashion_TMLIBCOM', 'bat-tmintegracionlaboratorios' : 'inditexcodingfashion_BATINTLA', 'bat-testingmanagementmailcompradores' : 'inditexcodingfashion_BATCHTESMANMAICOM', 'bat-testingmanagementcreacionexpedientes' : 'inditexcodingfashion_BATCHTESTMANEXP', 'bat-bloqueosseguridadsalud' : 'inditexcodingfashion_BATBLQSS', 'wsc-herramientacomprarss' : 'inditexcodingfashion_SEWHCRSS'},
             'Bloqueos' : {'mic-compliance': 'inditexcodingfashion_MICCOMPLIA',  'bat-compliance': 'inditexcodingfashion_BATCOMPLIA'},
             'PSM' : {'bat-joinlifemg': 'inditexcodingfashion_JLMGTBATCH', 'mic-firstordermaster' : 'inditexcodingfashion_FIRSTORDER', 'mic-joinlifemanagement' : 'inditexcodingfashion_JLMGTMIC', 'mic-joinliferequirements' : 'inditexcodingfashion_JLREQMIC', 'mic-psmdatareplicator' : 'inditexcodingfashion_PSMDATAREP', 'mic-validationcertif' : 'inditexcodingfashion_VALCERT', 'spa-joinlifemanagement' : 'inditexcodingfashion_JLMGTWEB'},
             'VSC' : {'mic-icbfspch' : 'inditexcodingfashion_ICBFSPCH', 'mlb-icmmspchios' : 'inditexcodingfashion_MLBSPCHIOS', 'mob-icmcspchios' : 'inditexcodingfashion_MOBSPCHIOS', 'spa-icmfspch' : 'inditexcodingfashion_ICMFSPCH'},
             'LQC' : {'mic-icbflqc' : 'inditexcodingfashion_ICBFLQC', 'mob-icmclqcios' : 'inditexcodingfashion_ICMCLQCIOS', 'mlb-icmmlqcios' : 'inditexcodingfashion_ICMMLQCIOS'},
             'Calidad' : {"lib-measuretable" : "inditexcodingfashion_ICPRCPPMTL", "mic-icbffppcrt" : "inditexcodingfashion_ICBFFPPCRT", "mic-measurementapi" : "inditexcodingfashion_ICPRCPPMA", "mlb-icmmmeasureios" : "inditexcodingfashion_ICMMMEASUR", "mlb-icmmqualityios" : "inditexcodingfashion_ICMMQUALIT", "mob-icmcqualityios" : "inditexcodingfashion_ICMCQUALIT", "spa-icmffppcrt" : "inditexcodingfashion_ICMFFPPCRT"},
             'Purchase-Forecasting' : {'spa-icmfppmforecast' :	'inditexcodingfashion_ICMFPPMFOR', 'mic-icbfppmforecast': 'inditexcodingfashion_ICBFPPMFOR'},
             'Design-Pattern' : {'spa-icmfproductblueprints' : 'inditexcodingfashion_ICMFPRBP', 'mic-icbfproductblueprints' : 'inditexcodingfashion_ICBFPRBP', 'lib-icwlblueprintmeasuretable' :	'inditexcodingfashion_ICWLBPMT'},
             'FP-Grid': {'mic-icbffinishedproductgrid' : 'inditexcodingfashion_ICBFFPGRID', 'spa-icmffinishedproductgrid' : 'inditexcodingfashion_ICMFFPGRID'}}


jira_keys = {'PSM' : 'JOINLIFEMG', 
             'TM' : 'TESTGMANA', 
             'Bloqueos' : 'TRACEMUL', 
             'VSC' : 'ICPRFPSCVW', 
             'LQC' : 'ICPRLQC', 
             'Calidad' : 'ICPRFPPCRT',
             'Purchase-Forecasting' : 'ICPRFPPFOR',
             'Design-Pattern' : 'ICPRDPAT',
             'FP-Grid': 'ICPRFPGRID',
             }

### Information about metrics
columns_detail = {"Realibility" : "reliability_rating", "Maintainability" : "sqale_rating", "Security" : "security_rating", "Unit Coverage" : "coverage", "Mutation Coverage" : "mutation", "Integration Coverage" : "integration"}
columns = copy.deepcopy(columns_detail)
columns.update({"Scope Change" : "scope_change", "Committed vs Delivered" : "committed_vs_delivered", "Velocity" : "velocity", "Bugs Fix Time" : "bugs_fix_time"})


### Helper functions to print the report
def add_lines(lines, elements):
    line = " |"
    for element in elements:
        line += element + " |"
    line += "\n"
    lines.append(line)

def create_table(metrics_all_projects, first_column, columns):
    lines = [first_column]

    add_lines(lines, columns)
    column_divs = [":----:"]
    for colum in columns: 
        column_divs.append(":----:")
    add_lines(lines, column_divs)

    for artifact in metrics_all_projects.keys():
        summary = metrics_all_projects[artifact]["metrics"]
        line = ["**{}**".format(artifact)]
        for metric in columns.values():
            try:
                line.append("{}".format(summary[metric]))
            except:
                print("An exception occurred. All keys: {}".format(summary.keys()))
            
        add_lines (lines, line)
    return lines
        
def combine_metrics(first, metrics):
    for element in metrics:
        for project in element:
            for metric in element[project]["metrics"].keys():
                first[project]["metrics"][metric] = element[project]["metrics"][metric]
    return first

def combine_metrics_per_artifact(first, second):
    first = combine_metrics(first, [second])
    for project in second:
        for artifact in second[project]["detail"].keys():
            for metric in second[project]["detail"][artifact]["metrics"].keys():
                first[project]["detail"][artifact]["metrics"][metric] = second[project]["detail"][artifact]["metrics"][metric] 
    return first


def create_md_report(metrics, columns, quality_columns):
    """
    Multiplies two numbers and returns the result.

    Args:
        metrics (dict): Metrics for all projects. 
        columns (dict): Columns for the general table. 
        quality_columns (dict): Columns for the quality table with detailed information per artifact.

    Returns:
        list: Lines with the report in MarkDown language.
    """
    lines = create_table(metrics, "Project", columns)
    for project in metrics:
        lines.append("\n<details>\n<summary>{} Quality Info</summary>\n\n".format(project))
        lines += (create_table(metrics[project]["detail"], "Artifact", quality_columns))
        lines.append("\n</details>")
    return lines


def gather_all_metrics(projects_list):
    # Gather metrics
    list_of_artifacts = {}
    for project in projects_list:
        try: 
            list_of_artifacts[project] = artifacts[project]
        except:
            print("Project {} not found!".format(project))
            exit()
    projects_jira = {}
    for project in projects_list:
        projects_jira[project] = jira_keys[project]
    sonar_metrics =  gather_sonar_metrics(list_of_artifacts)
    github_metrics = gather_gh_metrics(list_of_artifacts)
    jira_sprint_metrics = gather_sprint_metrics(projects_jira)
    bugs_metrics = gather_bugs_time_metrics(projects_jira)

    # Combine metrics
    metrics = combine_metrics_per_artifact(sonar_metrics, github_metrics)
    metrics = combine_metrics(metrics, [jira_sprint_metrics, bugs_metrics])
    return metrics


def get_db_connection():
    conn = sqlite3.connect('database/projects.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_results(metrics):
    conn = get_db_connection()
    cursor=conn.cursor()
    for project in metrics: 
        params = [project]
        for metric in columns.values():
            params.append(metrics[project]["metrics"][metric])
        print(len(params))
        cursor.execute("INSERT INTO projects (project_name, reliability_rating, sqale_rating, security_rating, coverage, mutation, integration, scope_change, committed_vs_delivered, velocity, bugs_fix_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(params)
            )
        project_run_id = cursor.lastrowid
        for artifact in metrics[project]["detail"]:
            params = [artifact, project_run_id]
            for metric in columns_detail.values():
                params.append(metrics[project]["detail"][artifact]["metrics"][metric])
            print(len(params))
            cursor.execute("INSERT INTO artifacts (repo, project_run_id, reliability_rating, sqale_rating, security_rating, coverage, mutation, integration) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(params)
                )
        conn.commit()
    conn.close()

if __name__ == "__main__":
    # Script to print or save metrics for one or several projects
    # Usage:
    #   PrintMetrics [print] [ProjectA, ProjectB ...]
    #
    #   By default, results are saved in a database unless the parameter "print" is passed
    #   By default, all projects are measured unless a list of project names are passed
    #
    #   Example:
    #       PrintMetrics print PSM
    #       PrintMetrics Bloqueos VSC
    print_data = False
    print(sys.argv)
    if (len(sys.argv) > 1):
        if (sys.argv[1] == "print"):
            print_data = True
            list_of_projects = sys.argv[2:]
        else:
            list_of_projects = sys.argv[1:]
    else:
        list_of_projects = artifacts.keys()
    print("Gathering metrics for {}".format(list_of_projects))
    metrics = gather_all_metrics(list_of_projects)
    print(metrics)

    if (print_data):
        # Create and write the report
        lines = create_md_report(metrics, columns, columns_detail)
        with open("metrics_report.md", "w") as f:
            f.writelines(lines)
    else:
        save_results(metrics)