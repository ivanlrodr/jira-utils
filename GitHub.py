import json
import os
import re
import requests

token = os.getenv('GITHUB_TOKEN')
username = 'ivanlrodr'
owner = 'inditex'
base_url = 'https://api.github.com'
headers = {"Authorization" : "token {}".format(token)}
params = {"branch" : "develop", "conclusion" : "success"}
params_workflow = { "per_page": 100}
#repos = ['mic-validationcertif', 'bat-joinlifemg', 'wsc-seguridadsaludproducto', 'mic-icbfspch']
repos_per_project = {'VSC' : ['mic-icbfspch', 'mlb-icmmspchios', 'mob-icmcspchios', 'spa-icmfspch'],
                     'Bloqueos': ['mic-compliance'],
                     'PSM' : ['bat-joinlifemg','mic-firstordermaster','mic-joinlifemanagement','mic-joinliferequirements','mic-psmdatareplicator','mic-validationcertif','spa-joinlifemanagement'],
                     'TM' : ['bat-testgmana','lib-samplemgmt','mic-tmblockintegration','wsc-seguridadsaludproducto','wsc-testingmanagementservicios']
                    }
test_types = ['mutation', 'integration']
debug = 0

def debug_print(text):
    if debug:
        print(text)


def gather_gh_metrics(repos_per_project):
    metrics = {}
    for project in repos_per_project.keys():
        metrics[project] = {}
        metrics[project]["metrics"] = {}
        metrics[project]["detail"]= {}
       
        averages = {}
        for test_type in test_types:
            averages[test_type] = []
        for repo in repos_per_project[project]:
            metrics[project]["detail"][repo] = {}
            metrics[project]["detail"][repo]["metrics"]= {}
            for test_type in test_types:
                metrics[project]["detail"][repo]["metrics"][test_type] = "N/A"
                debug_print("Checking repo {}".format(repo))
                url = f"{base_url}/repos/{owner}/{repo}/actions/workflows"
                user_data = requests.get(url, headers=headers, params=params_workflow)
                response = user_data.json()
                debug_print("Workflows: {}".format(response["total_count"]))
                found = False
                for workflow in response["workflows"]:
                    if (workflow["name"].find(test_type)>=0 and workflow["name"].startswith("code")):
                        found = True
                        debug_print(workflow["name"])
                        annotation = get_annotations(repo, workflow)
                        value = "N/A"
                        if annotation:
                            value = extract_value (test_type, annotation['message'])
                            averages[test_type].append(value)
                            print("\t\tRepo {} has {} test of {}".format(repo, test_type, value))
                        else:
                            print("\t\tRepo {} has no {} test".format(repo, test_type))
                        metrics[project]["detail"][repo]["metrics"][test_type] = "{}".format(value)

                        
                if not found:
                    debug_print("For repo {} we could not find workflow for {} testing".format(repo, test_type))
                    for workflow in response["workflows"]:
                        debug_print(workflow["name"])
    
        for test_type in test_types:
            if len(averages[test_type]):
                result = "{:.0f}".format(sum(averages[test_type]) / len(averages[test_type]))
            else:
                result = "N/A"
            metrics[project]["metrics"][test_type] = result
            print("{}: {} test coverage ({}/{} artifacts): {}".format(project, test_type, len(averages[test_type]), len(repos_per_project[project]), result))
    return metrics

def extract_value (test_type, message):
    if (test_type == "integration"):
        values = re.findall('Coverage: (\d+\.\d+)', message)
    else:
        values = re.findall('Mutation Coverage: (\d+\.\d+)', message)
        if (len(values) == 0):
            values = re.findall('Mutation score \(Coverage Based\): (\d+\.\d+)', message)
        
    if (len(values) == 0):
        print("Couldn't find {} percentage in {}".format(test_type, message))
        return 0
    else:
        return round(float(values[0]))
    
def get_annotations(repo, workflow):
    debug_print("We have workflow id {}".format(workflow['id']))
    url = f"{base_url}/repos/{owner}/{repo}/actions/workflows/{workflow['id']}/runs"
    #print(url)
    user_data = requests.get(url, headers=headers, params=params)
    response = user_data.json()
    if (len(response["workflow_runs"])) == 0:
        return
    first = response["workflow_runs"][0]
    #print(response["total_count"])
    debug_print("We have run id {}".format(first['id']))
    #print("--{}--".format(first['id']))
    url = f"{base_url}/repos/{owner}/{repo}/actions/runs/{first['id']}/jobs"
    user_data = requests.get(url, headers=headers)
    response = user_data.json()

    for job in response["jobs"]:
        job_id = job["id"]
        debug_print("We have job id {}".format(job_id))
        #print(response)
        #for element in response.keys():
        #    print("{} -->{}".format(element, response[element]))

        #https://api.github.com/repos/inditex/bat-joinlifemg/actions/runs/11528777200/jobs
        url = f"{base_url}/repos/{owner}/{repo}/check-runs/{job_id}/annotations"
        user_data = requests.get(url, headers=headers)
        response = user_data.json()
        
        #for element in response["jobs"][0].keys():
        #    print("{} -->{}".format(element, response["jobs"][0][element]))
        
        for annotation in response:
            #print("#####{}".format(annotation['title']))
            if (annotation['title'].startswith("Results")):
                return annotation
        #    if (annotation['title'] == 'Results [pitest]'):
        #        chunks = annotation['message'].split("|")
        #        for chunk in chunks:
        #            if (chunk.find("Mutation Coverage") > -1):
        #                index = chunk.find(": ") + 2
        #                mutation = int(chunk[index:-5])
        #                print(mutation)
    return 

if __name__ == "__main__":
    gather_gh_metrics(repos_per_project)