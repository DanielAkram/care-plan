"""调用 Claude 生成 care plan。同步、非流式，最简实现。"""

import anthropic

# 从环境变量 ANTHROPIC_API_KEY 读取密钥
client = anthropic.Anthropic()

PROMPT_TEMPLATE = """You are a clinical pharmacist at a specialty pharmacy. \
Based on the patient information below, write a pharmacist care plan.

The care plan MUST contain exactly these four sections, in this order:
1. Problem list / Drug therapy problems (DTPs)
2. Goals (SMART)
3. Pharmacist interventions / plan
4. Monitoring plan & lab schedule

Output plain text only (no markdown formatting), suitable for printing and \
handing to the patient's care team.

Patient information:
- Patient name: {first_name} {last_name}
- MRN: {mrn}
- Referring provider: {provider_name} (NPI: {provider_npi})
- Primary diagnosis (ICD-10): {primary_diagnosis}
- Additional diagnoses (ICD-10): {additional_diagnoses}
- Medication (this order): {medication}
- Medication history: {medication_history}

Patient records:
{patient_records}
"""


def generate_care_plan(data: dict) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(**data)}],
    )
    # content 里可能有 thinking 块，只取 text 块
    return "".join(block.text for block in response.content if block.type == "text")
