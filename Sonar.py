import copy
import requests
from requests.auth import HTTPBasicAuth
import os
import urllib3
from GitHub import *
from JiraMetrics import *

columns_detail = {"Realibility" : "reliability_rating", "Maintainability" : "sqale_rating", "Security" : "security_rating", "Unit Coverage" : "coverage", "Mutation Coverage" : "mutation", "Integration Coverage" : "integration"}
columns = copy.deepcopy(columns_detail)
columns.update({"Scope Change" : "scope_change", "Committed vs Delivered" : "committed_vs_delivered", "Velocity" : "velocity", "Bugs Fix Time" : "bugs_fix_time"})

urllib3.disable_warnings()
metrics_string = 'reliability_rating,sqale_rating,security_rating,coverage'
metrics_string_array = metrics_string.split(',')
metrics_to_convert = ['reliability_rating','sqale_rating','security_rating']
token = os.getenv('SONAR_TOKEN')

test_url = 'https://sonarcloud.io/api/measures/component'


def gather_sonar_metrics(projects):
    conversion_to_letters = {"1" :"A", "2" : "B", "3" : "C", "4" : "D", "5" : "E"}
    all_results = {}
    for project in projects:
        metrics_per_project = {}
        all_results[project] = {}
        all_results[project]["detail"] = {}
        for metric in metrics_string_array:
            metrics_per_project[metric] = 0
        for artifact in projects[project].keys():
            PARAM = {'component': projects[project][artifact], 
                    'metricKeys': metrics_string}
            # Retrieve the metrics from Sonar per repository
            test_response = requests.get(test_url, auth=HTTPBasicAuth(username=token, password=""), verify=False,params=PARAM)
            response_json = test_response.json()
            metrics_per_artifact = {}
            for metric in response_json['component']['measures']:
                value = round(float(metric['value']))
                metrics_per_project[metric['metric']] += value
                value = "{}".format(value)
                if metric['metric'] in metrics_to_convert:
                    value = conversion_to_letters[value]      
                metrics_per_artifact[metric['metric']] = value
            
            all_results[project]["detail"][artifact] = {}
            all_results[project]["detail"][artifact]["metrics"] = metrics_per_artifact

        for metric in metrics_string_array:
            metrics_per_project[metric] = "{:.0f}".format(metrics_per_project[metric]/len(projects[project].keys()))
            if metric in metrics_to_convert: 
                metrics_per_project[metric] = conversion_to_letters[metrics_per_project[metric]]

        all_results[project]["metrics"] = metrics_per_project
    return all_results


if __name__ == "__main__":
    bloqueos_artifacts = {'Bloqueos' : {'mic-compliance': 'inditexcodingfashion_MICCOMPLIA'}}
    sonar_metrics =  gather_sonar_metrics(bloqueos_artifacts)
    print(sonar_metrics)