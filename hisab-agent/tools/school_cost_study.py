"""
دراسة تكاليف المشاريع التعليمية — روضة + ابتدائي + متوسط
School project cost-feasibility tool (Saudi context, SAR)
"""
from fastmcp import FastMCP
from pydantic import BaseModel, Field

router = FastMCP(name="school")


# ──────────────────────────────────────────────
# Input models
# ──────────────────────────────────────────────

class LandInput(BaseModel):
    area_sqm: float = Field(default=10_000, description="مساحة الأرض م²")
    price_per_sqm: float = Field(default=1_500, description="سعر المتر SAR")


class CapacityInput(BaseModel):
    kindergarten_students: int = Field(default=120, description="عدد طلاب الروضة")
    elementary_students: int = Field(default=400, description="عدد طلاب الابتدائي")
    middle_students: int = Field(default=300, description="عدد طلاب المتوسط")


class FeeInput(BaseModel):
    kindergarten_annual: float = Field(default=18_000, description="رسوم الروضة السنوية SAR")
    elementary_annual: float = Field(default=15_000, description="رسوم الابتدائي السنوية SAR")
    middle_annual: float = Field(default=20_000, description="رسوم المتوسط السنوية SAR")


class BuildingInput(BaseModel):
    cost_per_sqm: float = Field(default=3_000, description="تكلفة البناء SAR/م²")
    kindergarten_area: float = Field(default=1_500, description="مساحة مبنى الروضة م²")
    elementary_area: float = Field(default=4_000, description="مساحة مبنى الابتدائي م²")
    middle_area: float = Field(default=3_000, description="مساحة مبنى المتوسط م²")
    infrastructure_pct: float = Field(default=0.15, description="نسبة البنية التحتية من تكلفة البناء")


class StaffInput(BaseModel):
    # معلمون
    teachers_count: int = Field(default=55, description="إجمالي عدد المعلمين")
    avg_teacher_salary: float = Field(default=7_500, description="متوسط راتب المعلم الشهري SAR")
    # إداريون ودعم
    admin_count: int = Field(default=12, description="عدد الموظفين الإداريين")
    avg_admin_salary: float = Field(default=5_500, description="متوسط راتب الإداري الشهري SAR")
    # عمالة مساندة
    support_count: int = Field(default=20, description="عدد عمالة النظافة والأمن والصيانة")
    avg_support_salary: float = Field(default=2_800, description="متوسط راتب العمالة المساندة الشهري SAR")


# ──────────────────────────────────────────────
# Tools
# ──────────────────────────────────────────────

@router.tool()
def calculate_capex(
    land: LandInput,
    building: BuildingInput,
) -> dict:
    """
    حساب التكاليف الرأسمالية (CAPEX) للمشروع:
    الأرض + البناء + التجهيزات + الترخيص.
    """
    land_cost = land.area_sqm * land.price_per_sqm

    construction_total = building.cost_per_sqm * (
        building.kindergarten_area
        + building.elementary_area
        + building.middle_area
    )
    infrastructure = construction_total * building.infrastructure_pct

    # تجهيزات وأثاث: 15 % من البناء
    furniture_equipment = construction_total * 0.15
    # تقنية تعليمية (سبورات ذكية، مختبرات، شبكة): 8 %
    technology = construction_total * 0.08
    # ملاعب وبيئة خارجية: 5 %
    outdoor = construction_total * 0.05
    # تراخيص وإشعارات وتصاميم هندسية: 3 %
    licenses_design = construction_total * 0.03
    # احتياطي طوارئ: 10 %
    contingency = (construction_total + infrastructure + furniture_equipment
                   + technology + outdoor + licenses_design) * 0.10

    capex_items = {
        "الأرض": round(land_cost),
        "أعمال البناء": round(construction_total),
        "البنية التحتية (طرق، شبكات)": round(infrastructure),
        "الأثاث والتجهيزات": round(furniture_equipment),
        "التقنية التعليمية": round(technology),
        "الملاعب والمساحات الخارجية": round(outdoor),
        "التراخيص والتصاميم الهندسية": round(licenses_design),
        "احتياطي الطوارئ (10%)": round(contingency),
    }
    total = sum(capex_items.values())
    capex_items["إجمالي CAPEX"] = total

    return {
        "تفاصيل_البناء": {
            "مساحة_الروضة_م2": building.kindergarten_area,
            "مساحة_الابتدائي_م2": building.elementary_area,
            "مساحة_المتوسط_م2": building.middle_area,
            "إجمالي_المساحة_المبنية_م2": building.kindergarten_area + building.elementary_area + building.middle_area,
            "تكلفة_البناء_م2": building.cost_per_sqm,
        },
        "بنود_التكلفة": capex_items,
        "إجمالي_CAPEX_SAR": total,
        "إجمالي_CAPEX_مليون_SAR": round(total / 1_000_000, 2),
    }


@router.tool()
def calculate_opex(
    capacity: CapacityInput,
    staff: StaffInput,
) -> dict:
    """
    حساب التكاليف التشغيلية السنوية (OPEX):
    رواتب + مرافق + صيانة + تسويق + تأمين.
    """
    total_students = capacity.kindergarten_students + capacity.elementary_students + capacity.middle_students

    # رواتب شاملة بدلات ومزايا (+25 %)
    teachers_annual = staff.teachers_count * staff.avg_teacher_salary * 12 * 1.25
    admin_annual = staff.admin_count * staff.avg_admin_salary * 12 * 1.25
    support_annual = staff.support_count * staff.avg_support_salary * 12 * 1.10
    total_salaries = teachers_annual + admin_annual + support_annual

    # تشغيل ومرافق
    utilities = total_students * 900          # كهرباء + ماء + إنترنت: 900 SAR/طالب/سنة
    maintenance = total_students * 600         # صيانة: 600 SAR/طالب/سنة
    consumables = total_students * 400         # مستلزمات تعليمية ومكتبية
    marketing = total_students * 500           # تسويق وقبول
    insurance = total_students * 300           # تأمين على المنشأة والطلاب
    transport_admin = 80_000                   # تشغيل سيارات إدارية

    opex_items = {
        "رواتب المعلمين (شاملة البدلات)": round(teachers_annual),
        "رواتب الإداريين": round(admin_annual),
        "رواتب العمالة المساندة": round(support_annual),
        "المرافق (كهرباء/ماء/إنترنت)": round(utilities),
        "الصيانة الدورية": round(maintenance),
        "المستلزمات التعليمية والمكتبية": round(consumables),
        "التسويق والقبول": round(marketing),
        "التأمين": round(insurance),
        "تشغيل إداري متفرق": round(transport_admin),
    }
    total = sum(opex_items.values())
    opex_items["إجمالي OPEX السنوي"] = total

    return {
        "عدد_الطلاب": {
            "روضة": capacity.kindergarten_students,
            "ابتدائي": capacity.elementary_students,
            "متوسط": capacity.middle_students,
            "الإجمالي": total_students,
        },
        "بنود_التكلفة": opex_items,
        "إجمالي_OPEX_SAR": total,
        "إجمالي_OPEX_مليون_SAR": round(total / 1_000_000, 2),
        "تكلفة_الطالب_السنوية": round(total / total_students),
    }


@router.tool()
def calculate_revenue(
    capacity: CapacityInput,
    fees: FeeInput,
    occupancy_rate: float = Field(default=0.85, description="نسبة الإشغال المتوقعة (0-1)"),
) -> dict:
    """حساب الإيرادات السنوية المتوقعة من الرسوم الدراسية."""
    kg = capacity.kindergarten_students * occupancy_rate * fees.kindergarten_annual
    el = capacity.elementary_students * occupancy_rate * fees.elementary_annual
    mid = capacity.middle_students * occupancy_rate * fees.middle_annual

    total = kg + el + mid
    other_revenue = total * 0.05   # أنشطة / مقصف / خدمات إضافية

    return {
        "نسبة_الإشغال": f"{occupancy_rate * 100:.0f}%",
        "إيرادات_الروضة": round(kg),
        "إيرادات_الابتدائي": round(el),
        "إيرادات_المتوسط": round(mid),
        "إيرادات_أخرى (أنشطة/مقصف)": round(other_revenue),
        "إجمالي_الإيرادات_SAR": round(total + other_revenue),
        "إجمالي_الإيرادات_مليون_SAR": round((total + other_revenue) / 1_000_000, 2),
    }


@router.tool()
def full_feasibility_study(
    land: LandInput,
    building: BuildingInput,
    capacity: CapacityInput,
    staff: StaffInput,
    fees: FeeInput,
    occupancy_rate: float = 0.85,
    discount_rate: float = 0.10,
    project_years: int = 15,
) -> dict:
    """
    دراسة الجدوى المالية الكاملة للمشروع التعليمي:
    CAPEX + OPEX + الإيرادات + نقطة التعادل + فترة الاسترداد + NPV + IRR تقريبي.
    """
    # ── CAPEX ──
    land_cost = land.area_sqm * land.price_per_sqm
    construction = building.cost_per_sqm * (
        building.kindergarten_area + building.elementary_area + building.middle_area
    )
    infra = construction * building.infrastructure_pct
    extras = construction * (0.15 + 0.08 + 0.05 + 0.03)
    contingency = (construction + infra + extras) * 0.10
    capex = land_cost + construction + infra + extras + contingency

    # ── OPEX ──
    total_students = capacity.kindergarten_students + capacity.elementary_students + capacity.middle_students
    salaries = (
        staff.teachers_count * staff.avg_teacher_salary * 12 * 1.25
        + staff.admin_count * staff.avg_admin_salary * 12 * 1.25
        + staff.support_count * staff.avg_support_salary * 12 * 1.10
    )
    opex = salaries + total_students * (900 + 600 + 400 + 500 + 300) + 80_000

    # ── Revenue ──
    revenue = (
        capacity.kindergarten_students * occupancy_rate * fees.kindergarten_annual
        + capacity.elementary_students * occupancy_rate * fees.elementary_annual
        + capacity.middle_students * occupancy_rate * fees.middle_annual
    ) * 1.05   # +5% إيرادات أخرى

    # ── Profitability ──
    gross_profit = revenue - opex
    gross_margin = gross_profit / revenue * 100 if revenue else 0

    # ── Break-even (years) ──
    payback_years = capex / gross_profit if gross_profit > 0 else None

    # ── NPV (+ قيمة بقايا الأرض) ──
    npv = -capex
    for yr in range(1, project_years + 1):
        cf = gross_profit * (1.03 ** yr)   # نمو 3% سنوياً
        npv += cf / ((1 + discount_rate) ** yr)
    npv += land_cost / ((1 + discount_rate) ** project_years)   # الأرض تحتفظ بقيمتها

    # ── IRR (binary search between -50% and +200%) ──
    def _npv_at(rate):
        v = -capex
        for yr in range(1, project_years + 1):
            v += gross_profit * (1.03 ** yr) / ((1 + rate) ** yr)
        # قيمة بقايا الأرض في نهاية المشروع
        v += land_cost / ((1 + rate) ** project_years)
        return v

    irr = None
    if gross_profit > 0:
        lo, hi = -0.5, 2.0
        if _npv_at(lo) * _npv_at(hi) < 0:
            for _ in range(60):
                mid_r = (lo + hi) / 2
                if _npv_at(mid_r) > 0:
                    lo = mid_r
                else:
                    hi = mid_r
            irr = (lo + hi) / 2

    status = "مجدي ✓" if npv > 0 and gross_profit > 0 else "غير مجدي ✗"

    return {
        "ملخص_المشروع": {
            "إجمالي_الطلاب": total_students,
            "نسبة_الإشغال": f"{occupancy_rate*100:.0f}%",
            "عمر_المشروع_سنة": project_years,
        },
        "الإيرادات_السنوية_SAR": round(revenue),
        "OPEX_السنوي_SAR": round(opex),
        "صافي_الربح_التشغيلي_السنوي_SAR": round(gross_profit),
        "هامش_الربح_الإجمالي_%": round(gross_margin, 1),
        "CAPEX_الإجمالي_SAR": round(capex),
        "فترة_الاسترداد_سنة": round(payback_years, 1) if payback_years else "—",
        "NPV_SAR": round(npv),
        "IRR_%": f"{irr*100:.1f}%" if irr else "—",
        "الحكم_على_المشروع": status,
        "تحليل_الحساسية": {
            "عند_إشغال_70%": _sensitivity(capex, opex, capacity, fees, staff, 0.70),
            "عند_إشغال_85%": _sensitivity(capex, opex, capacity, fees, staff, 0.85),
            "عند_إشغال_100%": _sensitivity(capex, opex, capacity, fees, staff, 1.00),
        },
    }


def _sensitivity(capex, opex, capacity, fees, staff, occ):
    rev = (
        capacity.kindergarten_students * occ * fees.kindergarten_annual
        + capacity.elementary_students * occ * fees.elementary_annual
        + capacity.middle_students * occ * fees.middle_annual
    ) * 1.05
    profit = rev - opex
    pb = round(capex / profit, 1) if profit > 0 else "خسارة"
    return {
        "إيرادات_SAR": round(rev),
        "صافي_ربح_SAR": round(profit),
        "فترة_استرداد_سنة": pb,
    }
