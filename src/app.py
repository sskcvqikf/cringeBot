from flask import Flask
from flask import request
from flask import jsonify

import requests
import json

import os

from dataclasses import dataclass


app = Flask(__name__)

BaseURL = "https://api.telegram.org"
DvangoToken = os.environ["DvangoToken"]
URL = f"{BaseURL}/bot{DvangoToken}"


@dataclass
class Request:
    chat_id: int
    req_message: str = ""
    resp_message: str = None
    
    def get_response_json(self):
        return {"chat_id": self.chat_id, "text": self.resp_message}


def send_message(r: Request):
    smURL = f"{URL}/sendMessage"
    resp = requests.post(smURL, json=r.get_response_json())
    return resp.json()


def handle_message(r: Request):
    r.resp_message = r.req_message  


def handle_error(r: Request):
    if r.req_message == "text":
        r.resp_message = "you are supposed to send text. im the text bot, so use me properly, baka."
    else:
        r.resp_message = "lol i dunno what to do with this stuff you send"


@app.route(f"/{DvangoToken}", methods=["POST", "GET"])
def handler():
    if request.method == "POST":
        jsn = request.get_json()
        chat_id = jsn["message"]["chat"]["id"]
        
        try:
            text = jsn["message"]["text"]
        except:
            r = Request(chat_id, "text")
            print(f"Got no text error from {r.chat_id}")
            handle_error(r)
            sended = send_message(r)
            return jsonify(sended)

        r = Request(chat_id, text)
        print(f"Got {r.req_message} from {r.chat_id}") 
        handle_message(r)
        sended = send_message(r)
        return jsonify(sended)
    else:
        return "yoooo how did u find this url?"


def main():
    app.run()
    

if __name__ == "__main__":
    main()
