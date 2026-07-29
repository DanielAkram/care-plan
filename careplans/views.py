import itertools

from django.http import Http404, HttpResponse
from django.shortcuts import render

from .llm import generate_care_plan

# 内存存储：{order_id: {...表单字段, "care_plan": str}}。重启进程即清空。
ORDERS = {}
_next_id = itertools.count(1)

FIELDS = [
    "first_name",
    "last_name",
    "mrn",
    "provider_name",
    "provider_npi",
    "primary_diagnosis",
    "additional_diagnoses",
    "medication",
    "medication_history",
    "patient_records",
]


def order_form(request):
    if request.method == "POST":
        data = {f: request.POST.get(f, "") for f in FIELDS}
        print(f"[1] 收到请求：patient={data['first_name']} {data['last_name']}, med={data['medication']}")

        # 同步等待 LLM 生成（通常几十秒），生成完直接展示
        print("[2] 开始调用 LLM ...")
        data["care_plan"] = generate_care_plan(data)
        print(f"[3] LLM 返回，care_plan 长度 = {len(data['care_plan'])} 字符")

        order_id = next(_next_id)
        ORDERS[order_id] = data
        return render(
            request,
            "careplans/result.html",
            {"order_id": order_id, "order": data},
        )
    return render(request, "careplans/form.html", {"orders": ORDERS})


def download_care_plan(request, order_id):
    order = ORDERS.get(order_id)
    if order is None:
        raise Http404("Order not found")
    response = HttpResponse(order["care_plan"], content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="care_plan_{order_id}.txt"'
    return response
