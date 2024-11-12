import json
from base64 import b64encode
from datetime import datetime
from typing import Any, Iterable

from dotenv import load_dotenv
from icalendar import Calendar, Event  # type:ignore[import-untyped]
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

SAMPLE_MODE = False

SAMPLE_RESULT = """\
[
    {
        "summary": "プロトタイピングA",
        "description": "組み込みシステム1 - Raspberry Pi とLED/センサーを組み合わせたシステムとWebサービスの連携",
        "dtstart": "20230530T180000",
        "dtend": "20230530T210000",
        "location": "奈良先端大"
    },
    {
        "summary": "イノベーション創出特論1",
        "description": "GEIOT基礎１ - パネル：先端科学技術事業化の潮流と重要性、概要先端科学技術ベンチャーの現在、ビジネスモデルキャンバス、チームわけ、アイスブレーク",
        "dtstart": "20230601T103000",
        "dtend": "20230601T175000",
        "location": "MOBIO"
    }
]\
"""

load_dotenv(override=True)


def _load_prompt() -> str:
    now = datetime.now()
    date = now.strftime("%m/%d")
    return f"""\
画像に含まれる予定情報から「summary」、「description」、「dtstart」、「dtend」、「location」を読み取ってください。
予定情報に年がなく月日のみ含まれる場合、月日が{date}より前なら{now.year+1}を、{date}以降なら{now.year}を年として設定してください。
返却形式はJSONで、valueにevents、keyに予定情報の配列を持つオブジェクトを返してください。
複数ある場合は配列に新たな要素として追加します。
読み取れない項目がある場合、そのvalueは空にしてください。
画像に予定情報が含まれない場合はerrorを返してください。"""


def _call_openai_api(
    prompt: str, messages: Iterable[ChatCompletionMessageParam]
) -> Any:
    client = OpenAI()
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    content = res.choices[0].message.content
    if content is None:
        raise ValueError("ChatGPT response is None")
    return json.loads(content)


def pick_schedule_from_text(text: str) -> Any:
    if SAMPLE_MODE:
        return json.loads(SAMPLE_RESULT)
    try:
        prompt = _load_prompt()
        messages: Iterable[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "text", "text": text},
                ],
            }
        ]
        return _call_openai_api(prompt, messages)
    except Exception as e:
        return {"error": str(e)}


def pick_schedule_from_image(image: bytes) -> Any:
    if SAMPLE_MODE:
        return json.loads(SAMPLE_RESULT)
    try:
        base64_image = b64encode(image).decode("utf-8")
        prompt = _load_prompt()
        messages: Iterable[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
        return _call_openai_api(prompt, messages)
    except Exception as e:
        return {"error": str(e)}


def json_to_ics(json_data: Any) -> str:
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    if not isinstance(json_data, list):
        raise ValueError("JSON data must be a list of events")
    cal = Calendar()
    for item in json_data:
        event = Event()
        event.add("summary", item.get("summary", ""))
        event.add("description", item.get("description", ""))
        event.add(
            "dtstart", datetime.strptime(item.get("dtstart", ""), "%Y-%m-%dT%H:%M:%S")
        )
        event.add(
            "dtend", datetime.strptime(item.get("dtend", ""), "%Y-%m-%dT%H:%M:%S")
        )
        event.add("location", item.get("location", ""))
        cal.add_component(event)
    return str(cal.to_ical().decode("utf-8"))
