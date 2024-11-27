DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS artifacts;

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    project_name TEXT NOT NULL,
    reliability_rating TEXT, 
    sqale_rating TEXT,
    security_rating TEXT,
    coverage TEXT,
    mutation TEXT, 
    integration TEXT,
    scope_change TEXT,
    committed_vs_delivered TEXT,
    velocity TEXT,
    bugs_fix_time TEXT,
    warnings TEXT
);

CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    project_run_id INTEGER NOT NULL, 
    repo TEXT,
    reliability_rating TEXT, 
    sqale_rating TEXT,
    security_rating TEXT,
    coverage TEXT,
    mutation TEXT, 
    integration TEXT,
    warnings TEXT,
    FOREIGN KEY (project_run_id) REFERENCES Projects(id)
);