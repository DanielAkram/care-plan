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
        # 同步等待 LLM 生成（通常几十秒），生成完直接展示
        data["care_plan"] = generate_care_plan(data)
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
