from dataclasses import dataclass
from flask import Flask, request, render_template
import requests

@dataclass
class User:
    auth: str
    name: str


users: list[User] = []


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


if __name__ == '__main__':
    app.run(debug=True)
