import json

from mistralai.client import Mistral

from app.llm.prompt import SYSTEM_PROMPT

from app.config.cfg import settings

import time


# ====================================================================================================
# ВЫЗОВ ЛЛМКИ (МИСТРАЛ)
# ====================================================================================================

def _call_llm(findings_batch_json, retries=3):
    api_key = settings.mistral_key
    if not api_key:
        raise RuntimeError("MISTRAL_KEY не найден")

    print("Размер батча в байтах:", len(findings_batch_json.encode('utf-8')))

    client = Mistral(api_key=api_key)

    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": findings_batch_json}
                ]
            )
            break
        except Exception as e:
            error_text = str(e)
            time.sleep(3)

    raw_text = response.choices[0].message.content.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"Не удалось распарсить ответ модели: {e}")
        print(f"Сырой ответ: {raw_text[:500]}")
        return []

# =====================================================================================================
# САМ ПРОЦЕСС АНАЛИЗА ЛЛМКОЙ, БАТЧАМИ
# ====================================================================================================

def analyze(findings_json) :

    findings = json.loads(findings_json)

    if not findings:
        return []

    BATCH_SIZE = 3

    all_results = []

    for i in range(0, len(findings), BATCH_SIZE) :

        batch = findings[i:i + BATCH_SIZE]

        batch_json = json.dumps(batch, ensure_ascii=False)

        batch_result = _call_llm(batch_json)
        all_results.extend(batch_result)

        time.sleep(2)

    return all_results



