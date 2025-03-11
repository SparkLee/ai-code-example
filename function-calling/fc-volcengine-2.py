"""
多轮function call代码示例

Usage:
pip install --upgrade "volcengine-python-sdk[ark]"

参考：
https://www.volcengine.com/docs/82379/1262342#python-3
"""
import json
import os
import time

from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ApiKeyVolcengine 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ApiKeyVolcengine"),
)

tool_list = [
    {
        "type": "function",
        "function": {
            "name": "MusicPlayer",
            "description": "歌曲查询Plugin，当用户需要搜索某个歌手或者歌曲时使用此plugin，给定歌手，歌名等特征返回相关音乐",
            "parameters": {
                "properties": {
                    "artist": {"description": "表示歌手名字", "type": "string"},
                    "description": {
                        "description": "表示描述信息",
                        "type": "string",
                    },
                    "song_name": {
                        "description": "表示歌曲名字",
                        "type": "string",
                    },
                },
                "required": [],
                "type": "object",
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "GetCurrentWeather",
            "description": "查询当前的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "地理位置，比如北京市",
                    },
                    "unit": {"type": "string", "description": "单位类型",
                             "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "LinkReaderPlugin",
            "description": "当需要解析网页内容时，调用本插件",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "需要解析网页链接,最多3个；",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "WebSearchPlugin",
            "description": "当需要搜索互联网内容时，调用本插件",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "需要搜索的内容",
                    },
                },
                "required": ["keywords"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "SendMessage",
            "description": "需要发送微信消息时，使用本函数",
            "parameters": {
                "type": "object",
                "properties": {
                    "receiver": {
                        "type": "string",
                        "description": "接受对象",
                    },
                    "content": {
                        "type": "string",
                        "description": "需要发送的内容",
                    },
                },
                "required": ["receiver"],
            },
        },
    },
]


def LinkReaderPlugin(argument: dict):
    import requests

    urls = argument["url"]
    resp_text = []
    # if type(urls)==list:
    for url in urls:
        resp = requests.get(f"https://r.jina.ai/{url}")
        print(f"API[r.jina.ai]请求响应结果：", resp)
        resp_text.append(resp.text.partition("Markdown Content:")[2])
    print("===============\n".join(resp_text))
    return "===============\n".join(resp_text)


TOOL_RESPONSE = {
    "GetCurrentWeather": lambda argument: f"{argument['location']}今天20~24度，天气：阵雨。",
    "SendMessage": lambda argument: f"成功发送微信消息至{argument['receiver']}",
    "LinkReaderPlugin": LinkReaderPlugin,
    "WebSearchPlugin": lambda
        argument: f"{argument['keywords'].split(' ')[0]} 是一个开源项目，创立于2022年12日7日，主要目的是方便大家使用Transformer并加速人工智能技术的发展",
}


def request(req):
    completion = client.chat.completions.create(**req)
    if completion.choices[0].message.tool_calls:
        #  FunctionCall response
        req["messages"].append(completion.choices[0].message.model_dump())
    else:
        # Normal response (no FunctionCall)
        req["messages"].append(
            {
                "role": completion.choices[0].message.role,
                "content": completion.choices[0].message.content,
            }
        )
    return req


def test_function_call():
    round_num = 1
    req = {
        "model": "doubao-1-5-pro-32k-250115",
        "messages": [
            {
                "role": "user",
                "content": "先查询北京的天气，如果是晴天微信发给Alan，否则发给Peter",
            },
        ],
        "temperature": 0.8,
        "tools": tool_list,
    }
    while True:
        if req["messages"][-1]["role"] == "assistant":
            if "tool_calls" in req["messages"][-1]:
                tool_name = req["messages"][-1]["tool_calls"][0]["function"]["name"]
                req["messages"].append(
                    {
                        "role": "tool",
                        "tool_call_id": req["messages"][-1]["tool_calls"][0]["id"],
                        "content": TOOL_RESPONSE[tool_name](
                            json.loads(
                                req["messages"][-1]["tool_calls"][0]["function"][
                                    "arguments"
                                ]
                            )
                        ),  # 根据实际调用函数结果填写，最好用自然语言。
                        "name": tool_name,
                    }
                )
                pass
            else:
                query = input("human:").strip()
                req["messages"].append(
                    {
                        "role": "user",
                        "content": f"""{query}""",
                    }
                )

        ts = time.time()
        req = request(req)
        print("=" * 10 + f" Round {round_num} " + "=" * 10)
        print(
            f"\033[31m{req['messages'][-2]['role']}\033[0m: {req['messages'][-2]['content'][:50] + '...'}\n"
        )
        if "tool_calls" in req["messages"][-1]:
            # FC
            _flag = "[FC Response]"
            _resp = f"name={req['messages'][-1]['tool_calls'][0]['function']['name']}, args={req['messages'][-1]['tool_calls'][0]['function']['arguments']}"
        else:
            # No FunctionCall
            if len(req["messages"]) >= 3 and req["messages"][-2]["role"] == "tool":
                _flag = "[Final Answer]"
            else:
                _flag = "[Normal Response]"
            _resp = req["messages"][-1]["content"]
        round_num += 1
        print(
            f"\033[31massistant\033[0m \033[34m{_flag}\033[0m:\n{_resp} \n[elpase={time.time() - ts:.3f} s]"
        )


if __name__ == '__main__':
    test_function_call()
