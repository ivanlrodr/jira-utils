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

jiraOptions = {'server': "https://jira.inditex.com/jira/"} 
# You can introduce your own user and password in the next two lines
# user = "usuario@ext.inditex.com"
# password = "yourPassword"
user = os.getenv('USUARIO')
password = os.getenv('PASSWORD')

jira = JIRA(options=jiraOptions, basic_auth=(user, password)) 

MAX_RESULTS = 500
SECONDS_PER_DAY = 86400
DAYS_TO_CHECK = 90
DEPLOYMENT_DATE = "customfield_19361"
projects = ['JOINLIFEMG','TESTGMANA', 'TRACEMUL', 'ICPRFPSCVW']
priority_types = ['"A++(Bloqueo)"', '"A+(Crítico)", "A(Muy Importante)"',
                  '"B(Importante)", "C(Menor)"']

for project in projects:
    for priority in priority_types: 
        # Find all issues for a given priority for a given proyect
        issues = jira.search_issues(jql_str='project = {} AND issuetype = Bug AND '
            'created > startOfDay(-{}) AND resolution = Fixed AND '
            'status != "To deploy" AND priority in ({}) '
            'order by priority DESC'.format(project, DAYS_TO_CHECK, priority), 
                                    maxResults=MAX_RESULTS)
        print('{}: bug types ({}) during last {} days. Number of '
            'incidences {}'.format(project, priority, DAYS_TO_CHECK, len(issues)))
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
            #print('{} Priority: {} Date: {} deployed {} -- days to solve {}'.format(issue.key, 
            # issue.fields.priority, issue.fields.created, issue.get_field(DEPLOYMENT_DATE), 
            # time_delta.total_seconds()/SECONDS_PER_DAY, issue.fields.summary))
        if (days_to_solve > 0):
            print('{}: bug types ({}) during last {} days. Time to resolution: '
                '{:.2f} days\n'.format(project,
                priority, DAYS_TO_CHECK, days_to_solve/len(issues)))
        else:
            print()