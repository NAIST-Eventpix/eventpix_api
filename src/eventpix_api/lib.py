import json
from base64 import b64encode
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

SAMPLE_MODE = True

PROMPT_IMAGE = """\
画像に含まれる予定情報から「summary」、「description」、「dtstart」、「dtend」、「location」を読み取ってください。
その後、ルート要素を配列にしたJSONで返してください。
複数ある場合は配列に新たな要素として追加します。
読み取れない項目がある場合、そのvalueは空にしてください。
画像に予定情報が含まれない場合はerrorを返してください。\
"""

SAMPLE_RESULT_IMAGE = """\
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

PROMPT_TEXT = """\
テキストに含まれる予定情報から「summary」、「description」、「dtstart」、「dtend」、「location」を読み取ってください。
その後、ルート要素を配列にしたJSONで返してください。
複数ある場合は配列に新たな要素として追加します。
読み取れない項目がある場合、そのvalueは空にしてください。
画像に予定情報が含まれない場合はerrorを返してください。\
"""

SAMPLE_RESULT_TEXT = """\
[
    {
        "summary": "プロジェクト会議",
        "description": "",
        "dtstart": "20231113T100000",
        "dtend": "",
        "location": "東京オフィス"
    }
]\
"""

load_dotenv(override=True)


# 画像の予定抽出
def pick_schedule_from_image(image: bytes) -> Any:
    try:
        if SAMPLE_MODE:
            return json.loads(SAMPLE_RESULT_IMAGE)

        base64_image = b64encode(image).decode("utf-8")

        client = OpenAI()
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": PROMPT_IMAGE,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = res.choices[0].message.content

        if content is None:
            raise ValueError("ChatGPT response is None")

        result_json = json.loads(content)

        return result_json

    except Exception as e:
        return {"error": str(e)}


# テキストの予定抽出
def pick_schedule_from_text(text: str) -> Any:
    try:
        if SAMPLE_MODE:
            return json.loads(SAMPLE_RESULT_TEXT)

        client = OpenAI()
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": PROMPT_TEXT + "\n\n" + text,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = res.choices[0].message.content

        # OpenAI APIのレスポンス判定
        if not content:
            raise ValueError("OpenAI API からのレスポンスが空です")

        # JSONデコード処理
        try:
            result_json = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("OpenAI API からのレスポンスが不正な JSON 形式です")

        return result_json

    except Exception as e:
        return {"error": str(e)}
