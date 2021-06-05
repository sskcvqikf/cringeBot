from flask import Flask
from flask import request
from flask import jsonify

import requests
import json
import yaml

import os

from dataclasses import dataclass

from flashtext.keyword import KeywordProcessor
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch


app = Flask(__name__)

BaseURL = "https://api.telegram.org"
DvangoToken = os.environ["DvangoToken"]
URL = f"{BaseURL}/bot{DvangoToken}"

tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

keyword_processor = KeywordProcessor()
contexts = {}


@dataclass
class Request:
    chat_id: int
    req_message: str = None
    resp_message: str = None

    def get_response_json(self):
        return {"chat_id": self.chat_id, "text": self.resp_message}


def read_file(filename: str) -> str:
    with open(filename, mode="r") as f:
        content = f.read()
    return content


def add_to_keyword_processor(keyword: str, sinonyms: list[str], filename: str):
    contexts[keyword] = read_file(filename)
    for i in sinonyms:
        keyword_processor.add_keyword(i, keyword)


def get_context(string_to_search: str) -> str:
    keywords_found = keyword_processor.extract_keywords(string_to_search)
    if not keywords_found:
        return 
    return contexts[keywords_found[0]]


def get_answer(question: str, context: str) -> str:
    inputs = tokenizer(question, context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]
    outputs = model(**inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits
    answer_start = torch.argmax(
        answer_start_scores
    ) 
    answer_end = torch.argmax(answer_end_scores) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer


def send_message(r: Request):
    smURL = f"{URL}/sendMessage"
    resp = requests.post(smURL, json=r.get_response_json())
    return resp.json()


def handle_message(r: Request):
    context = get_context(r.req_message)
    if context is None:
        r.resp_message = "I am question-ansering bot. I dont support basic questions like 'how are you' or 'hello'. Also, I dont support questions from topics, that are not in my database."
        return
    r.resp_message = get_answer(r.req_message, context)


def handle_error(r: Request):
    r.resp_message = "I support only text messages. No pictures, no editing, no deleting."


def get_chat_id(jsn: dict) -> int:
    if "message" in jsn:
        return jsn["message"]["chat"]["id"]
    if "edited_message" in jsn:
        return jsn["edited_message"]["chat"]["id"]


def get_text(jsn: dict) -> str:
    text = jsn["message"]["text"]
    return text


@app.route(f"/{DvangoToken}", methods=["POST", "GET"])
def handler():
    if request.method == "POST":
        jsn = request.get_json()
        chat_id = get_chat_id(jsn)
        r = Request(chat_id)
        try:
            text = get_text(jsn)
        except:
            handle_error(r)
            return jsonify(send_message(r))
        r.req_message = text
        print(f"Got {r.req_message} from {r.chat_id}") 
        handle_message(r)
        sended = send_message(r)
        return jsonify(sended)
    else:
        return "Get is not supported"


def load_data():
    _, _, file_names = next(os.walk('contexts'))
    keyword_synonims_files = {}
    for file_name in file_names:
        with open(f"./contexts/{file_name}") as f:
            loaded = yaml.load(f, Loader=yaml.FullLoader)
        add_to_keyword_processor(loaded["name"], loaded["synonyms"], f"./contexts/data/{loaded['file']}")


@app.before_first_request
def _init():
    load_data()

def main():
    app.run()

if __name__ == "__main__":
    main()
