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


conf   = load_conf()
gitlab = Gitlab(conf['url'], private_token=conf['private-token'], per_page=100)


