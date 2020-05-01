from local_settings import PROJECTS_PATH
import os
import json

if not os.path.isdir(PROJECTS_PATH):
    os.makedirs(PROJECTS_PATH)

PROJECTS = json.load(open("projects.json", "r"))

for project in PROJECTS:
    if not os.path.isdir(f"{PROJECTS_PATH}/repos/{project['slug']}"):
        os.system(f"git clone -b {project['branch']} {project['git']} {PROJECTS_PATH}/repos/{project['slug']}")

    os.system(f"cd {PROJECTS_PATH}/repos/{project['slug']}; doxygen {PROJECTS_PATH}/repos/{project['slug']}/Doxyfile")

    if not os.path.exists(f"{PROJECTS_PATH}/{project['slug']}"):
        os.system(f"ln -s {PROJECTS_PATH}/repos/{project['slug']}/docs/Doxygen/html {PROJECTS_PATH}/{project['slug']}")

