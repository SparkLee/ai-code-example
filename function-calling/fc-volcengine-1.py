"""
单轮function call代码示例

Usage:
pip install --upgrade "volcengine-python-sdk[ark]"

参考：
https://www.volcengine.com/docs/82379/1262342#python-2
"""
import json
import os
import time

import requests
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ApiKeyVolcengine 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ApiKeyVolcengine"),
)


def test_function_call():
    messages = [
        {
            "role": "system",
            # "content": "你是调皮可爱的天气预报员",
            "content": "你是一位语言精炼，沉稳的的天气预报员",
        },
        {
            "role": "user",
            "content": "我今天想去广州玩一下，想知道天气如何？",
        },
    ]
    req = {
        "model": "doubao-1-5-pro-32k-250115",  # 模型ID（ModelId）或接入点ID（EndpointId）
        "messages": messages,
        "temperature": 0.8,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "MusicPlayer",
                    "description": """歌曲查询Plugin，当用户需要搜索某个歌手或者歌曲时使用此plugin，给定歌手，歌名等特征返回相关音乐。\n 例子1：query=想听孙燕姿的遇见， 输出{"artist":"孙燕姿","song_name":"遇见","description":""}""",
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
                    "name": "get_current_weather",
                    "description": "",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "地理位置，比如北京市",
                            },
                            "unit": {"type": "string", "description": "枚举值 [摄氏度,华氏度]"},
                        },
                        "required": ["location"],
                    },
                },
            },
        ],
    }

    ts = time.time()
    completion = client.chat.completions.create(**req)
    completion_message = completion.choices[0].message
    if completion_message.tool_calls:
        tool_call = completion_message.tool_calls[0]
        print(
            f"Bot [{time.time() - ts:.3f} s][Use FC]: ",
            tool_call,
        )
        location = json.loads(tool_call.function.arguments)["location"]
        print(f"待查询城市：", location)
        # ========== 补充函数调用的结果 =========
        req["messages"].extend(
            [
                completion_message.model_dump(),
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    # "content": "北京天气晴，24~30度",  # 根据实际调用函数结果填写，最好用自然语言。
                    "content": get_weather(location),
                    "name": tool_call.function.name,
                },
            ]
        )
        # 再请求一次模型，获得总结。 如不需要，也可以省略
        ts = time.time()
        completion = client.chat.completions.create(**req)
        print(
            f"Bot [{time.time() - ts:.3f} s][FC Summary]: ",
            completion.choices[0].message.content,
        )


def get_weather(location: str) -> str:
    """
    调用公开免费的天气查询API查询天气信息（Open-Meteo is an open-source weather API and offers free access for non-commercial use. No API key required. Start using it now!）
    :param location:
    :return:
    """

    # 地理编码（北京中心坐标）
    params = {
        "latitude": get_coordinates_local(location)[0],
        "longitude": get_coordinates_local(location)[1],
        "current": "temperature_2m,weather_code",
        "timezone": "auto",
        "forecast_days": 1
    }

    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        data = response.json()
        # print(data)

        # 解析天气代码（示例映射，完整代码需参考open-meteo文档）
        weather_code_map = {
            0: "晴", 1: "晴", 2: "多云", 3: "阴",
            45: "雾", 48: "霜", 51: "小雨", 61: "中雨"
        }

        current = data["current"]
        weather_desc = weather_code_map.get(current["weather_code"], "未知天气")
        temperature = current["temperature_2m"]
        unit = data["current_units"]["temperature_2m"]

        result = f"{location}{weather_desc}，气温{temperature}{unit}"
        print(f"天气查询API结果：", result)
        return result

    except Exception as e:
        print(f"天气查询失败: {str(e)}")
        return f"{location}天气信息暂不可用"


def get_coordinates_local(city: str) -> tuple:
    city_coordinates = {
        "北京市": (39.9042, 116.4074),
        "上海市": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "广州市": (23.1291, 113.2644),
    }
    return city_coordinates.get(city)

if __name__ == '__main__':
    test_function_call()
