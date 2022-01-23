import requests
import json

from main.config.slack import SLACK_WEBHOOK_URL

class Slack:
    @staticmethod
    def notify(message: str):
        requests.post(SLACK_WEBHOOK_URL, json.dumps({
                    "text" : message,
                }))
