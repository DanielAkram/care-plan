import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from .llm import generate_care_plan
from .models import CarePlan, Order, Patient, Provider

# 每个文件拿自己的 logger，名字就是模块名。以后看 log 能一眼知道哪个文件打的。
logger = logging.getLogger(__name__)

# 表单会 POST 上来的字段
FIELDS = [
    "first_name",
    "last_name",
    "dob",
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
        logger.info("[1] 收到请求：patient=%s %s, med=%s",
                    data["first_name"], data["last_name"], data["medication"])

        # 1) 患者：同 MRN 已存在就复用，不存在才新建（get_or_create）
        #    这实现了你设计的"一个患者、多个订单"——第二单复用同一 Patient。
        patient, _ = Patient.objects.get_or_create(
            mrn=data["mrn"],
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "dob": data["dob"],
            },
        )

        # 2) 医生：同 NPI 已存在就复用
        provider, _ = Provider.objects.get_or_create(
            npi=data["provider_npi"],
            defaults={"name": data["provider_name"]},
        )

        # 3) 订单：存进 Order 表，外键指向上面的患者和医生
        order = Order.objects.create(
            patient=patient,
            provider=provider,
            medication=data["medication"],
            primary_diagnosis=data["primary_diagnosis"],
            additional_diagnoses=data["additional_diagnoses"],
            medication_history=data["medication_history"],
            patient_records=data["patient_records"],
        )

        # 4) 同步调用 LLM 生成
        logger.info("[2] 开始调用 LLM ...")
        content = generate_care_plan(data)
        logger.info("[3] LLM 返回，care_plan 长度 = %d 字符", len(content))

        # 5) care plan 存进 CarePlan 表，状态直接 completed（Day 4 才会用异步状态流转）
        CarePlan.objects.create(
            order=order, content=content, status=CarePlan.Status.COMPLETED
        )

        return render(request, "careplans/result.html", {"order": order})

    # GET 首页：从数据库读所有订单，最新的在前
    # select_related 一次性把关联的 patient 也查出来，避免循环里逐条查库(N+1)
    orders = Order.objects.select_related("patient").order_by("-created_at")
    return render(request, "careplans/form.html", {"orders": orders})


def download_care_plan(request, order_id):
    # 从数据库取订单；取不到自动返回 404
    order = get_object_or_404(Order, id=order_id)
    content = order.care_plan.content   # 通过外键反向拿到 CarePlan 的正文
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="care_plan_{order_id}.txt"'
    return response


def get_order(request, order_id):
    # 从数据库查，查不到返回 JSON 格式的 404（保持 API 一致性）
    try:
        order = Order.objects.select_related("patient", "care_plan").get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({
        "order_id": order.id,
        "patient": f"{order.patient.first_name} {order.patient.last_name}",
        "medication": order.medication,
        "care_plan": order.care_plan.content,
    })
