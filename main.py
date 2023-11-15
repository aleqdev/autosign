from dataclasses import dataclass

import apscheduler.jobstores.base
from flask import Flask, request, render_template
import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


@dataclass
class User:
    auth: str
    name: str


user_auth = str
event_id = int
job = object


@dataclass
class Dispatch:
    auths: list[user_auth]
    job: job


users: list[User] = []
scheduler = BackgroundScheduler()
dispatches: dict[event_id, Dispatch] = {}


scheduler.start()
app = Flask(__name__)


@app.route("/")
def index():
    print("get", users)
    return render_template('index.html', users=users)


@app.route("/adduser", methods=["POST"])
def adduser():
    content = request.json

    print("add", content["name"], content["auth"])

    users.append(
        User(
            auth=content["auth"],
            name=content["name"]
        )
    )

    return "ok"


@app.route("/enroll", methods=["POST"])
def enroll():
    content = request.json

    print("enroll", content["id"], content["auth"])

    url = f"https://online.sochisirius.ru/schedule?mobile&task=enroll&id={content['id']}"
    headers = {'authorization': content["auth"]}

    resp = requests.post(url, headers=headers)

    print(resp)

    return resp.content


@app.route("/unenroll", methods=["POST"])
def unenroll():
    content = request.json

    print("unenroll", content["id"], content["auth"])

    url = f"https://online.sochisirius.ru/schedule?mobile&task=unEnroll&id={content['id']}"
    headers = {'authorization': content["auth"]}

    resp = requests.post(url, headers=headers)

    print(resp)

    return resp.content


@app.route("/getinfo", methods=["POST"])
def getinfo():
    content = request.json

    print("getinfo", content["auth"])

    url = f"https://online.sochisirius.ru/schedule?mobile&task=getSchedule&rec=true&begin=14.11.2023&end=28.11.2023"
    headers = {'authorization': content["auth"]}

    resp = requests.post(url, headers=headers)
    j = resp.json()

    print(j)

    return j


@app.route("/adddispatch", methods=["POST"])
def adddispatch():
    content = request.json

    auth = content["auth"]
    id = content["id"]
    date_time = content["datetime"]

    run_time = datetime.strptime(date_time, '%d.%m.%Y %H:%M:%S')

    dispatch = dispatches.get(id, None)

    if dispatch is None:
        job = scheduler.add_job(dispatch_enroll, 'date', run_date=run_time, timezone='Europe/Moscow', args=[id])
        dispatches[id] = Dispatch(auths=[auth], job=job)
    else:
        dispatch.auths.append(auth)

    return "ok"


@app.route("/removedispatch", methods=["POST"])
def removedispatch():
    content = request.json

    auth = content["auth"]
    id = content["id"]

    dispatch = dispatches.get(id, None)

    if dispatch:
        if auth in dispatch.auths:
            dispatch.auths.remove(auth)
            if len(dispatch.auths) == 0:
                try:
                    dispatch.job.remove()
                except apscheduler.jobstores.base.JobLookupError:
                    pass

                dispatches.pop(id)

    return "ok"


@app.route("/dispatches", methods=["GET"])
def getdispatches():
    return [
        (k,v.auths) for k, v in dispatches.items()
    ]


def dispatch_enroll(event_id):
    print("dispatch_enroll: ", datetime.now(), event_id)

    for _ in range(3):
        for _ in range(20):
            for auth in dispatches[event_id].auths:
                url = f"https://online.sochisirius.ru/schedule?mobile&task=enroll&id={event_id}"
                headers = {'authorization': auth}
                print(auth, " - ", requests.post(url, headers=headers).content)

            time.sleep(0.05)
        time.sleep(2)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
