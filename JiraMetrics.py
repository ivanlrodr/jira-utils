"""
Description: Script to demonstrate how to interact with Jira using Python
Dependencies: Python3, package installer "pip" and the module "jira". 
Install:
    * Python3: https://www.python.org/downloads/
    * pip: https://pip.pypa.io/en/stable/installation/
    * jira module: pip install jira
Author: Ivan Lopez Rodriguez
"""
from datetime import datetime
from jira import JIRA
import os

INITIAL_POINTS_FIELD_NAME = "customfield_19377"
FINISHED_POINTS_FIELD_NAME = "customfield_19378"
ADDED_POINTS_FIELD_NAME = "customfield_35462"
REMOVED_POINTS_FIELD_NAME = "customfield_35463"
jiraOptions = {'server': "https://jira.inditex.com/jira/"}
# You can introduce your own user and password in the next two lines
# user = "ivanlrodr@ext.inditex.com"
# password = "yourPassword"
user = os.getenv('USUARIO')
password = os.getenv('PASSWORD')

jira = JIRA(options=jiraOptions, basic_auth=(user, password))

MAX_SPRINTS = 6
MAX_RESULTS = 500
SECONDS_PER_DAY = 86400
DAYS_TO_CHECK = 90
DEPLOYMENT_DATE = "customfield_19361"
#projects_to_jira = {'PSM' : 'JOINLIFEMG','TM' : 'TESTGMANA', 'Bloqueos' : 'TRACEMUL', 'VSC' : 'ICPRFPSCVW', 'LQC' : 'ICPRLQC', 'Calidad' : 'ICPRFPPCRT'}
priority_types = {'"A++(Bloqueo)"' : "B", '"A+(Crítico)", "A(Muy Importante)"' : "H",
                  '"B(Importante)", "C(Menor)"': "L"}


def gather_sprint_metrics(projects):
    results = {}

    for project in projects:
        results[project] = {}
        results[project]["metrics"] = {}
        jira_project_name = projects[project]
        issues = jira.search_issues(jql_str='project = {} AND issuetype = "Sprint Report" '
            'and "Sprint State" ~ Closed '
            'order by created DESC'.format(jira_project_name), maxResults=MAX_SPRINTS)
        velocity = 0
        scope_change = 0
        commited_vs_delivered = 0
        for issue in issues:
            initial_points = issue.get_field(INITIAL_POINTS_FIELD_NAME)
            finished_points = issue.get_field(FINISHED_POINTS_FIELD_NAME)
            velocity += finished_points
            commited_vs_delivered += finished_points/initial_points*100
            added_points = issue.get_field(ADDED_POINTS_FIELD_NAME)
            removed_points = issue.get_field(REMOVED_POINTS_FIELD_NAME)
            scope_change += (initial_points - removed_points + added_points)/initial_points*100
            #print("For sprint {} we had {} initial points, added {} removed {} initial/commited {:.2f} and scope change {:.2f}".format(issue.fields.summary,
            #  initial_points, added_points, finished_points, finished_points/initial_points*100, 
            # (initial_points - removed_points + added_points)/initial_points*100))
        results[project]["metrics"]["scope_change"] = "{:.2f}%".format(scope_change/MAX_SPRINTS-100)
        results[project]["metrics"]["committed_vs_delivered"] = "{:.2f}%".format(commited_vs_delivered/MAX_SPRINTS)
        results[project]["metrics"]["velocity"] = "{:.0f}".format(velocity/MAX_SPRINTS)

        print("{}\t scope change {:.2f}% \tcommitted vs delivered {:.2f}% and \tvelocity {:.2f}".format(jira_project_name,
            scope_change/MAX_SPRINTS-100, commited_vs_delivered/MAX_SPRINTS, velocity/MAX_SPRINTS))
    return results



def gather_bugs_time_metrics(projects):
    results = {}
    for project in projects:
        jira_project = projects[project]
        results[project]={}
        results[project]["metrics"] = {}
        result_text = ""
        for priority in priority_types.keys():

            # Find all issues for a given priority for a given proyect
            issues = jira.search_issues(jql_str='project = {} AND issuetype = Bug AND '
                'created > startOfDay(-{}) AND resolution = Fixed '
                'AND "Entorno Incidencia" = Produccion AND status != "To deploy" '
                'AND priority in ({}) '
                'order by priority DESC'.format(jira_project, DAYS_TO_CHECK, priority), 
                                        maxResults=MAX_RESULTS)

            print('{}: bug types ({}) during last {} days. Number of '
                'incidences {}'.format(jira_project, priority, DAYS_TO_CHECK, len(issues)))
            days_to_solve = 0
            for issue in issues: 
                # Find how long every issue took to be fixed
                # created_date example from Jira: 2024-09-12T11:28:18.200
                created_date = issue.fields.created.replace("T", " ").split('.')[0]
                # created_date example after replacing and splitting: 2024-09-12 11:28:18
                created_date = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                
                try:
                    # We prefer "deployed date" but, if itsn't there, we take resolution date
                    deployed_date = issue.get_field(DEPLOYMENT_DATE)
                    if (not deployed_date):
                        deployed_date = issue.get_field("resolutiondate")
                    deployed_date = deployed_date.replace("T", " ").split('.')[0]
                    deployed_date = datetime.strptime(deployed_date, '%Y-%m-%d %H:%M:%S')
                except Exception as error:
                    print('An error occurred dealing with ticket '
                        '{}\n\t{}'.format(issue.key, error))
                    quit()
                
                time_delta = deployed_date - created_date
                days_to_solve += time_delta.total_seconds()/SECONDS_PER_DAY
                #if priority == '"A++(Bloqueo)"':
                #    print('{} Priority: {} Date: {} deployed {} -- days to solve {}'.format(issue.key, 
                #     issue.fields.priority, issue.fields.created, issue.get_field(DEPLOYMENT_DATE), 
                #     time_delta.total_seconds()/SECONDS_PER_DAY, issue.fields.summary))
            if (days_to_solve > 0):
                #print('{}: bug types ({}) during last {} days. Time to resolution: '
                #    '{:.2f} days\n'.format(project,
                #    priority, DAYS_TO_CHECK, days_to_solve/len(issues)))
                result_text += "{} {:.2f}d; ".format(priority_types[priority], days_to_solve/len(issues))
            else:
                #print()
                result_text += "{} {}; ".format(priority_types[priority], "N/A")
        results[project]["metrics"]["bugs_fix_time"] = result_text[:-2]
    return results


if __name__ == "__main__":
    projects = {'Bloques' : 'TRACEMUL'}
    sprint_metrics = gather_sprint_metrics(projects)
    print(sprint_metrics)
    bug_metrics = gather_bugs_time_metrics(projects)
