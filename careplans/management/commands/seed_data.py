"""
往数据库塞一些假数据，方便在 TablePlus 里看效果。
运行：docker compose exec web python manage.py seed_data

故意设计：Sarah Chen 有 3 个订单（对应手册"张三看病 5 次"）——
你会在 order 表里看到 3 行的 patient_id 都指向同一个患者，
但 patient 表里 Sarah 只存了一行。这就是外键去重的效果。
"""

from datetime import date

from django.core.management.base import BaseCommand

from careplans.models import CarePlan, Order, Patient, Provider


class Command(BaseCommand):
    help = "Seed the database with mock patients, providers, orders, and care plans."

    def handle(self, *args, **options):
        # 幂等：先清空，避免重复跑时 MRN/NPI 冲突
        CarePlan.objects.all().delete()
        Order.objects.all().delete()
        Patient.objects.all().delete()
        Provider.objects.all().delete()

        # ---- 患者（每人只存一次）----
        sarah = Patient.objects.create(
            first_name="Sarah", last_name="Chen", mrn="048192", dob=date(1971, 3, 22)
        )
        marcus = Patient.objects.create(
            first_name="Marcus", last_name="Delgado", mrn="051337", dob=date(1965, 11, 8)
        )
        alice = Patient.objects.create(
            first_name="Alice", last_name="Bennett", mrn="012345", dob=date(1979, 6, 8)
        )

        # ---- 医生（每人只存一次）----
        raman = Provider.objects.create(name="Dr. Priya Raman, MD (Rheumatology)", npi="1467589302")
        rodriguez = Provider.objects.create(name="Dr. Maya Rodriguez, MD (Neurology)", npi="1234567893")

        # ---- 订单：Sarah 一人开了 3 单，全指向同一个 patient ----
        o1 = Order.objects.create(
            patient=sarah, provider=raman,
            medication="Adalimumab (Humira) 40 mg SC",
            primary_diagnosis="M05.79", additional_diagnoses="E11.9, Z79.4",
            medication_history="Methotrexate 20 mg weekly\nPrednisone 5 mg daily",
            patient_records="Seropositive RA, DAS28 5.4. Adding biologic.",
        )
        o2 = Order.objects.create(
            patient=sarah, provider=raman,
            medication="Methotrexate 25 mg PO weekly",
            primary_diagnosis="M05.79", additional_diagnoses="",
            medication_history="Prior MTX 20 mg weekly",
            patient_records="Dose escalation visit.",
        )
        o3 = Order.objects.create(
            patient=sarah, provider=raman,
            medication="Folic acid 1 mg PO daily",
            primary_diagnosis="M05.79", additional_diagnoses="",
            medication_history="",
            patient_records="Supportive therapy alongside MTX.",
        )
        # 另外两个患者各一单
        o4 = Order.objects.create(
            patient=marcus, provider=rodriguez,
            medication="IVIG (immune globulin intravenous)",
            primary_diagnosis="G70.00", additional_diagnoses="I10",
            medication_history="Pyridostigmine 60 mg q6h PRN",
            patient_records="Myasthenia gravis exacerbation. Weight 88 kg.",
        )
        o5 = Order.objects.create(
            patient=alice, provider=rodriguez,
            medication="Rituximab 1000 mg IV",
            primary_diagnosis="G70.00", additional_diagnoses="",
            medication_history="Failed steroids",
            patient_records="Refractory MG.",
        )

        # ---- Care plan：故意留不同状态，展示状态字段 ----
        CarePlan.objects.create(order=o1, status=CarePlan.Status.COMPLETED,
                                content="PHARMACIST CARE PLAN\n(已生成的完整内容...)")
        CarePlan.objects.create(order=o2, status=CarePlan.Status.COMPLETED,
                                content="PHARMACIST CARE PLAN\n(已生成...)")
        CarePlan.objects.create(order=o3, status=CarePlan.Status.PENDING, content="")
        CarePlan.objects.create(order=o4, status=CarePlan.Status.PROCESSING, content="")
        CarePlan.objects.create(order=o5, status=CarePlan.Status.FAILED,
                                content="", )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {Patient.objects.count()} patients, "
            f"{Provider.objects.count()} providers, "
            f"{Order.objects.count()} orders, "
            f"{CarePlan.objects.count()} care plans."
        ))
