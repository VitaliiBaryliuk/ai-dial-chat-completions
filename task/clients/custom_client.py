import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialCustomClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        self._headers = {
            'api-key': self._api_key,
            "Content-Type": 'application/json'
        }

    def get_completion(self, messages: list[Message]) -> Message:
        request = {
            'messages': [msg.to_dict() for msg in messages]
        }

        response = requests.post(url=self._endpoint, headers=self._headers, json=request)

        if response.status_code == 200:
            data = response.json()
            choices = data.get('choices', [])
            if choices:
                content = choices[0].get('message', {}).get('content')
                print(content)
                return Message(Role.AI, content)
        else:
            raise Exception('No choices found')


    async def stream_completion(self, messages: list[Message]) -> Message:
        request = {
            'stream': True,
            'messages': [msg.to_dict() for msg in messages]
        }

        contents = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=self._headers, json=request) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data = line_str[6:].strip()
                            if data != '[DONE]':
                                content = self._get_content_snippet(data)
                                print(content, end='')
                                contents.append(content)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(error_text)
                return Message(role = Role.AI, content = ''.join(contents))    

    def _get_content_snippet(self, data: str) -> str:
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''

