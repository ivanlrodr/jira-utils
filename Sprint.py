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

MAX_RESULTS = 6
projects = ['JOINLIFEMG','TESTGMANA', 'TRACEMUL', 'ICPRFPSCVW']       
    
for project in projects:
    issues = jira.search_issues(jql_str='project = {} AND issuetype = "Sprint Report" '
        'and "Sprint State" ~ Closed '
        'order by created DESC'.format(project), maxResults=6)
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
        #print("For sprint {} added {} removed {} initial/commited {} and scope change {}".format(issue.fields.summary,
        #  initial_points, finished_points, finished_points/initial_points*100, 
        # (initial_points - removed_points + added_points)/initial_points*100))
    print("{}\t scope change {:.2f}% \tcommitted vs delivered {:.2f}% and \tvelocity {:.2f}".format(project,
        scope_change/MAX_RESULTS-100, commited_vs_delivered/MAX_RESULTS, velocity/MAX_RESULTS))