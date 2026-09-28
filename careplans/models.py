"""
四张表，对应我们设计的四个资源(resource)。
每个 class = 一张表；每个字段 = 表的一列。
ForeignKey = 你想到的那根"引用线"(外键)。
"""

from django.db import models


class Patient(models.Model):
    """患者。信息只存一遍，被订单引用。"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mrn = models.CharField(max_length=6, unique=True)    # 严格按需求：unique 6-digit number
    dob = models.DateField()                              # 出生日期，必填(业务上是硬需求)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (MRN {self.mrn})"


class Provider(models.Model):
    """开药医生。信息也只存一遍，被订单引用。"""
    name = models.CharField(max_length=200)
    npi = models.CharField(max_length=10, unique=True)    # NPI 10 位、唯一

    def __str__(self):
        return f"{self.name} (NPI {self.npi})"


class Order(models.Model):
    """一个订单 = 一个患者 + 一种药 + 一次开方。"""
    # 外键：订单不存患者名字，只存"指向哪个患者"。患者改名，订单不用动。
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="orders")
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="orders")

    medication = models.CharField(max_length=200)
    primary_diagnosis = models.CharField(max_length=20)          # ICD-10
    additional_diagnoses = models.TextField(blank=True)          # 逗号分隔的 ICD-10
    medication_history = models.TextField(blank=True)
    patient_records = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)         # 自动记录创建时间

    def __str__(self):
        return f"Order #{self.id} — {self.patient.first_name} / {self.medication}"


class CarePlan(models.Model):
    """一个订单对应一份 care plan。带状态，是 Day 4 异步的前提。"""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    # OneToOne：一个订单只有一份 care plan
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="care_plan")
    content = models.TextField(blank=True)                       # LLM 生成的正文
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CarePlan for Order #{self.order_id} [{self.status}]"
