"""
阿里云-大模型服务平台百炼
Function Calling: https://help.aliyun.com/zh/model-studio/user-guide/qwen-function-calling
"""

## 步骤1:定义工具函数

# 添加导入random模块
import random
from datetime import datetime


# 模拟天气查询工具。返回结果示例：“北京今天是雨天。”
def get_current_weather(arguments):
    # 定义备选的天气条件列表
    weather_conditions = ["晴天", "多云", "雨天"]
    # 随机选择一个天气条件
    random_weather = random.choice(weather_conditions)
    # 从 JSON 中提取位置信息
    location = arguments["location"]
    # 返回格式化的天气信息
    return f"{location}今天是{random_weather}。"


# 查询当前时间的工具。返回结果示例：“当前时间：2024-04-15 17:15:18。“
def get_current_time():
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 格式化当前日期和时间
    formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # 返回格式化后的当前时间
    return f"当前时间：{formatted_time}。"


# 测试工具函数并输出结果，运行后续步骤时可以去掉以下四句测试代码
# print("测试工具输出：")
# print(get_current_weather({"location": "上海"}))
# print(get_current_time())
# print("\n")

## 步骤2:创建 tools 数组

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "当你想知道现在的时间时非常有用。",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"]
            }
        }
    }
]
# tool_name = [tool["function"]["name"] for tool in tools]
# print(f"创建了{len(tools)}个工具，为：{tool_name}\n")

## 步骤3:创建messages数组

messages = [
    {
        "role": "system",
        "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
     如果用户提问关于时间的问题，请调用‘get_current_time’函数。
     请以友好的语气回答问题。""",
    },
    {
        "role": "user",
        # "content": "上海天气"
        # "content": "现在几点钟了？"
        "content": "上海天气如何，现在上海是几点钟？"
        # "content": "你好"
    }
]
# print("messages 数组创建完成\n")

# 步骤4:发起 function calling

from openai import OpenAI
import os

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("ApiKeyAliyunDashscope"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def function_calling():
    _completion = client.chat.completions.create(
        model="qwen-plus",
        # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=messages,
        tools=tools
    )
    print("返回对象：")
    # print(_completion)
    print(_completion.choices[0].message.model_dump_json())
    print("\n")
    return _completion


print("正在发起function calling...")
completion = function_calling()
# print("===========================")
# print(completion)
# ChatCompletion(
#   id='chatcmpl-55d71445-8881-9090-b6ee-fc654a526524',
#   choices=[
#     Choice(
#       finish_reason='tool_calls',
#       index=0,
#       logprobs=None,
#       message=ChatCompletionMessage(
#           content='',
#           refusal=None,
#           role='assistant',
#           audio=None,
#           function_call=None,
#           tool_calls=[ChatCompletionMessageToolCall(
#                           id='call_24ef26db625a44d0b38fba',
#                           function=Function(arguments='{"location": "上海"}', name='get_current_weather'),
#                           type='function',
#                           index=0
#                        )
#                       ]
#       )
#     )
#   ],
#   created=1741670220,
#   model='qwen-plus',
#   object='chat.completion',
#   service_tier=None,
#   system_fingerprint=None,
#   usage=CompletionUsage(
#           completion_tokens=18,
#           prompt_tokens=276,
#           total_tokens=294,
#           completion_tokens_details=None,
#           prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0)
#   )
# )
# print("===========================")

# 步骤5:运行工具函数

import json

print("正在执行工具函数...")
# 从返回的结果中获取函数名称和入参
function_name = completion.choices[0].message.tool_calls[0].function.name
arguments_string = completion.choices[0].message.tool_calls[0].function.arguments

# 使用json模块解析参数字符串
arguments = json.loads(arguments_string)
# 创建一个函数映射表
function_mapper = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time
}
# 获取函数实体
function = function_mapper[function_name]
# 如果入参为空，则直接调用函数
if arguments == {}:
    function_output = function()
# 否则，传入参数后调用函数
else:
    function_output = function(arguments)
# 打印工具的输出
print(f"工具函数输出：{function_output}\n")

# 步骤6:向大模型提交工具输出

messages.append(completion.choices[0].message)
print("已添加assistant message")
messages.append(
    {"role": "tool", "content": function_output, "tool_call_id": completion.choices[0].message.tool_calls[0].id})
print("已添加tool message\n")

# 步骤7:大模型总结工具输出

print("正在总结工具输出...")
completion = function_calling()


# 步骤8:进阶用法-流式输出

def function_calling_stream():
    _messages = [
        {
            "role": "system",
            "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
         如果用户提问关于时间的问题，请调用‘get_current_time’函数。
         请以友好的语气回答问题。""",
        },
        {
            "role": "user",
            "content": "上海天气如何？"
        }
    ]
    _completion = client.chat.completions.create(
        model="qwen-plus",
        messages=_messages,
        tools=tools,
        stream=True
    )
    for chunk in _completion:
        print(chunk.model_dump_json())


print("正在发起 function_calling_stream ...")
function_calling_stream()
print("\n")


# 步骤9:进阶用法-指定工具调用方式-并行工具调用
# 上文中的问题“上海天气”只需经过一次工具调用即可得到准确回复，如果输入问题需要调用多次工具，如“四个直辖市的天气如何”或“杭州天气，以及现在几点了”，发起 Function Calling 后只会返回一个工具调用信息，
# 为了解决这一问题，您可以在发起 Function Calling时，将请求参数parallel_tool_calls设置为true，这样返回对象中将包含所有需要调用的工具函数与入参信息。

def function_calling_parallel_tool_calls():
    _messages = [
        {
            "role": "system",
            "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
         如果用户提问关于时间的问题，请调用‘get_current_time’函数。
         请以友好的语气回答问题。""",
        },
        {
            "role": "user",
            # "content": "上海天气如何，现在上海是几点钟？"
            "content": "四个直辖市的天气如何？"
        }
    ]
    _completion = client.chat.completions.create(
        model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=_messages,
        tools=tools,
        # 新增参数
        parallel_tool_calls=True
    )
    print("返回对象：")
    print(_completion.choices[0].message.model_dump_json())
    return _completion


print("正在发起 function_calling_parallel_tool_calls ...")
function_calling_parallel_tool_calls()
print("\n")


# 步骤10:进阶用法-指定工具调用方式-强制工具调用
# 大模型生成内容具有不确定性，有时会选择错误的工具进行调用。如果您希望对于某一类问题，大模型能够采取制定好的工具选择策略（如强制使用某个工具、强制使用至少一个工具、强制不使用工具等），可以通过修改tool_choice参数来强制指定工具调用的策略。
# tool_choice参数的默认值为"auto"，表示由大模型自主判断如何进行工具调用。

###（1） 强制使用某个工具
def function_calling_only_handle_one_specified_tool():
    _messages = [
        {
            "role": "system",
            "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
             如果用户提问关于时间的问题，请调用‘get_current_time’函数。
             请以友好的语气回答问题。""",
        },
        {
            "role": "user",
            "content": "长沙天气如何？"
        }
    ]
    _completion = client.chat.completions.create(
        model="qwen-plus",
        messages=_messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_current_weather"}} # 强制使用某个工具
        # tool_choice={"type": "function", "function": {"name": "get_current_time"}}
    )
    print(_completion.model_dump_json())


print("正在发起 function_calling_only_handle_one_specified_tool ...")
function_calling_only_handle_one_specified_tool()
print("\n")


###（2） 强制使用至少一个工具
def function_calling_must_use_at_least_one_tool():
    _messages = [
        {
            "role": "system",
            "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
                如果用户提问关于时间的问题，请调用‘get_current_time’函数。
                请以友好的语气回答问题。""",
        },
        {
            "role": "user",
            "content": "长沙天气如何？"
        }
    ]
    _completion = client.chat.completions.create(
        model="qwen-plus",
        messages=_messages,
        tools=tools,
        tool_choice="required" # 强制使用至少一个工具
    )
    print(_completion.model_dump_json())


print("正在发起 function_calling_must_use_at_least_one_tool ...")
function_calling_must_use_at_least_one_tool()
print("\n")

###（3）强制不使用工具
def function_calling_without_tool():
    _messages = [
        {
            "role": "system",
            "content": """你是一个很有帮助的助手。如果用户提问关于天气的问题，请调用 ‘get_current_weather’ 函数;
                    如果用户提问关于时间的问题，请调用‘get_current_time’函数。
                    请以友好的语气回答问题。""",
        },
        {
            "role": "user",
            "content": "长沙天气如何？"
        }
    ]
    _completion = client.chat.completions.create(
        model="qwen-plus",
        messages=_messages,
        tools=tools,
        tool_choice="none" # 强制不使用工具
    )
    print(_completion.model_dump_json())

print("正在发起 function_calling_without_tool ...")
function_calling_without_tool()
print("\n")