from gitlab import Gitlab
from pathlib import Path
import json


def list_all(gitlab_object):
    page = 0
    ret  = []

    while True:
        page_results = gitlab_object.list(page=page)

        print("%d: %s" % (page, page_results))

        if len(page_results) == 0:
            break

        ret.extend(page_results)
        page += 1

    return ret


def load_conf():
    with open("%s/.gitlab_conf.json" % Path.home(), "r") as f:
        ret = json.load(f)

    return ret


conf = load_conf()
gitlab = Gitlab(conf['url'], private_token=conf['private-token'], per_page=100)

for group_name in conf['groups']:
    group = gitlab.groups.get(group_name)

    projects = list_all(group.projects)

    print("\"%s\": {" % group_name)

    conf['groups'][group_name] = {}

    for project in projects:
        print("    \"%s\": %d," % (project.name, project.id))

        conf['groups'][group_name][project.name] = project.id

    print("},")

print(json.dumps(conf, indent=4))

with open("%s/.gitlab_conf.json" % Path.home(), "w") as f:
    json.dump(conf, f, indent=4)
