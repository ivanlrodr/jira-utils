import sys

from GitHub import *
from JiraMetrics import *
from Sonar import *

### Information about projects
artifacts = {'TM' : {'bat-testgmana' : 'inditexcodingfashion_TMBATCH', 'lib-samplemgmt': 'inditexcodingfashion_SAMPLEMGMT', 'mic-tmblockintegration': 'inditexcodingfashion_TMBLOCKINT', 'wsc-seguridadsaludproducto': 'inditexcodingfashion_SSPSWREST', 'wsc-testingmanagementservicios': 'inditexcodingfashion_TMSWREST'},
             'Bloqueos' : {'mic-compliance': 'inditexcodingfashion_MICCOMPLIA'},
             'PSM' : {'bat-joinlifemg': 'inditexcodingfashion_JLMGTBATCH', 'mic-firstordermaster' : 'inditexcodingfashion_FIRSTORDER', 'mic-joinlifemanagement' : 'inditexcodingfashion_JLMGTMIC', 'mic-joinliferequirements' : 'inditexcodingfashion_JLREQMIC', 'mic-psmdatareplicator' : 'inditexcodingfashion_PSMDATAREP', 'mic-validationcertif' : 'inditexcodingfashion_VALCERT', 'spa-joinlifemanagement' : 'inditexcodingfashion_JLMGTWEB'},
             'VSC' : {'mic-icbfspch' : 'inditexcodingfashion_ICBFSPCH', 'mlb-icmmspchios' : 'inditexcodingfashion_MLBSPCHIOS', 'mob-icmcspchios' : 'inditexcodingfashion_MOBSPCHIOS', 'spa-icmfspch' : 'inditexcodingfashion_ICMFSPCH'},
             'LQC' : {'mic-icbflqc' : 'inditexcodingfashion_ICBFLQC', 'mob-icmclqcios' : 'inditexcodingfashion_ICMCLQCIOS', 'mlb-icmmlqcios' : 'inditexcodingfashion_ICMMLQCIOS'},
             'Calidad' : {"lib-measuretable" : "inditexcodingfashion_ICPRCPPMTL", "mic-icbffppcrt" : "inditexcodingfashion_ICBFFPPCRT", "mic-measurementapi" : "inditexcodingfashion_ICPRCPPMA", "mlb-icmmmeasureios" : "inditexcodingfashion_ICMMMEASUR", "mlb-icmmqualityios" : "inditexcodingfashion_ICMMQUALIT", "mob-icmcqualityios" : "inditexcodingfashion_ICMCQUALIT", "spa-icmffppcrt" : "inditexcodingfashion_ICMFFPPCRT"}}

jira_keys = {'PSM' : 'JOINLIFEMG', 
             'TM' : 'TESTGMANA', 
             'Bloqueos' : 'TRACEMUL', 
             'VSC' : 'ICPRFPSCVW', 
             'LQC' : 'ICPRLQC', 
             'Calidad' : 'ICPRFPPCRT'}

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




if __name__ == "__main__":
    # Read optional list of projects
    if (len(sys.argv) > 1):
        list_of_artifacts = {}
        for project in sys.argv[1:]:
            try: 
                list_of_artifacts[project] = artifacts[project]
            except:
                print("Project {} not found!".format(project))
                exit()
    else:
        list_of_artifacts = artifacts

    # Gather metrics
    projects_jira = {}
    for project in list_of_artifacts:
        projects_jira[project] = jira_keys[project]
    sonar_metrics =  gather_sonar_metrics(list_of_artifacts)
    github_metrics = gather_gh_metrics(list_of_artifacts)
    jira_sprint_metrics = gather_sprint_metrics(projects_jira)
    bugs_metrics = gather_bugs_time_metrics(projects_jira)

    # Combine metrics
    metrics = combine_metrics_per_artifact(sonar_metrics, github_metrics)
    metrics = combine_metrics(metrics, [jira_sprint_metrics, bugs_metrics])
    print(metrics)

    # Create and write the report
    lines = create_md_report(metrics, columns, columns_detail)
    with open("metrics_report.md", "w") as f:
        f.writelines(lines)