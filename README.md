# jira-utils
Collection of python scripts to generate different reports per project using data from Jira, Github and Sonarcloud. 

## Prerequisites
* Python 3: https://www.python.org/downloads/
* Pip, a package installer: https://pypi.org/project/pip/
* Jira module:

    ```bash
    pip install jira
    ```

## Before Running the Scripts
You need to call the scripts using your username and password and personal tokens. The scripts read these information from environment variables so there are two options: create your own environment variables or overwriting these commands with your personal information. You will need to update user and password in *JiraMetrics.py*, the token for sonar in *Sonar.py* and the Github token in *GitHub.py*.

Before:

```python
user = os.getenv('USUARIO')
password = os.getenv('PASSWORD')
token = os.getenv('SONAR_TOKEN')
```
After:
```python
user = 'myUserName'
password = 'secretPassword'
token = 'xo3dñlxoxoo45'
```

You could also edit the list of projects with their artifacts (dictionary *artifacts*) and their Jira keys (dictionary *jira_keys*) in *PrintMetrics.py* to include any other projects:
```python
# artifacts = { 'Project Name' : { 'repo-name' : 'sonar-repo-name'}}
artifacts = {'Bloqueos' : {'mic-compliance': 'inditexcodingfashion_MICCOMPLIA'}}
# jira_keys = { 'Project Name' : 'jira-key''}
jira_keys = {'Bloqueos' : 'TRACEMUL'}
```

## Running the Scripts
Scripts can be called individually:
```bash
python3 JiraMetrics.py
```
The information for the projects included in the main function will be displayed:
```bash
ivan@PRT-ILOPEZ:~/repos/jira-utils$ python3 JiraMetrics.py 
TRACEMUL         scope change -2.58%    committed vs delivered 80.95% and       velocity 19.67
TRACEMUL: bug types ("A++(Bloqueo)") during last 90 days. Number of incidences 0
TRACEMUL: bug types ("A+(Crítico)", "A(Muy Importante)") during last 90 days. Number of incidences 1
TRACEMUL: bug types ("B(Importante)", "C(Menor)") during last 90 days. Number of incidences 5
```

## Reports
* **PrintMetrics**: generates a Markdown table with all metrics for all projects. The script also accepts project names as parameters:
```bash
ivan@PRT-ILOPEZ:~/repos/jira-utils$ python3 JiraMetrics.py Bloqueos
```
Example of the generated report *metrics_report.md*:

Project |Realibility |Maintainability |Security |Unit Coverage |Mutation Coverage |Integration Coverage |Scope Change |Committed vs Delivered |Velocity |Bugs Fix Time |
 |:----: |:----: |:----: |:----: |:----: |:----: |:----: |:----: |:----: |:----: |:----: |
 |**Bloqueos** |A |A |A |89 |71 |2 |-2.58% |80.95% |20 |B N/A; H 0.02d; L 0.20d |

<details>
<summary>Bloqueos Quality Info</summary>

Artifact |Realibility |Maintainability |Security |Unit Coverage |Mutation Coverage |Integration Coverage |
 |:----: |:----: |:----: |:----: |:----: |:----: |:----: |
 |**mic-compliance** |A |A |A |89 |71 |2 |

</details>

## Scripts
* **JiraMetrics**
    * Information about key metrics of the last 6 sprints:
        * Scope change: are tickets being added or removed after sprint has started?
        * Commited vs delivered: when the sprint finished, did the team finished all the tickets they committed to?
        * Velocity: how many story points the team is able to complete per sprint?
    * Information about the time to fix bugs by category.
* **GitHub**
    * Information about mutation and integration testing coverage (gather from Github).
* **Sonar**
    * Information about code quality and unit testing coverage (gather from SonarCloud). 
 
      
