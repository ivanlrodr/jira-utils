# jira-utils
Collection of python scripts to generate some reports from Jira. 

## Prerequisites
* Python 3: https://www.python.org/downloads/
* Pip, a package installer: https://pypi.org/project/pip/
* Jira module:

    ```bash
    pip install jira
    ```

## Before Running the Scripts
You need to call the scripts using your username and password. The scripts read these information from environment variables so there are two options: create your own environment variables or overwriting these commands with your user and password:

Before:

```python
user = os.getenv('USUARIO')
password = os.getenv('PASSWORD')
```
After:
```python
user = 'myUserName'
password = 'secretPassword'
```

You should also edit the list of projects and, instead of the given ones, add the Jira keys of your own projects:
```python
#projects = ['JOINLIFEMG','TESTGMANA', 'TRACEMUL', 'ICPRFPSCVW']
projects = ['MY_JIRA_PROJECT']
```

## Running the Scripts
It is enough to call them like the following example:
```bash
python3 Sprint.py
```
The information for your proeyects will be displayed:
```bash
ivan@PRT-ILOPEZ:~/repos/ivan$ /bin/python3 /home/ivan/repos/ivan/Sprint.py
JOINLIFEMG       scope change 10.38%    committed vs delivered 108.71% and      velocity 30.00
TESTGMANA        scope change 13.59%    committed vs delivered 66.89% and       velocity 27.50
TRACEMUL         scope change -3.09%    committed vs delivered 82.47% and       velocity 18.50
ICPRFPSCVW       scope change 4.13%     committed vs delivered 99.00% and       velocity 64.17
```

## Reports
* **Sprints**: a report about key metrics of the last 6 sprints:
    * Scope change: are tickets being added or removed after sprint has started?
    * Commited vs delivered: when the sprint finished, did the team finished all the tickets they committed to?
    * Velocity: how many story points the team is able to complete per sprint?
* **BugsTime**: prints the average time to fix a bug in production by priority.
    * Blocker: A++(Bloqueo)
    * High: A+(Crítico) A(Muy Importante)
    * Low: B(Importante) C(Minor)
 
      
