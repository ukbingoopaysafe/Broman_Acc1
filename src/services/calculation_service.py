
from decimal import Decimal

def calculate_sale_transaction(data: dict) -> dict:
    """
    Calculate all amounts for a sale based on Excel logic.

    Args:
        data: A dictionary containing all input fields for the sale.

    Returns:
        A dictionary containing all the calculated output fields.
    """

    # Extract inputs and convert to Decimal for precise calculations
    unit_price = Decimal(str(data.get("unit_price", 0)))
    company_commission_rate = Decimal(str(data.get("company_commission_rate", 0)))
    salesperson_commission_rate = Decimal(str(data.get("salesperson_commission_rate", 0)))
    salesperson_incentive_rate = Decimal(str(data.get("salesperson_incentive_rate", 0)))
    vat_rate = Decimal(str(data.get("vat_rate", 0.14)))  # Default 14%
    sales_tax_rate = Decimal(str(data.get("sales_tax_rate", 0.05)))  # Default 5%
    annual_tax_rate = Decimal(str(data.get("annual_tax_rate", 0.225)))  # Default 22.5%
    salesperson_tax_rate = Decimal(str(data.get("salesperson_tax_rate", 0)))
    sales_manager_tax_rate = Decimal(str(data.get("sales_manager_tax_rate", 0)))
    sales_manager_commission_rate = Decimal(str(data.get("sales_manager_commission_rate", 0)))

    # Calculations based on prompt2.txt

    # العمولة المستحقة للشركة من شركة المبيعات
    company_commission_amount = unit_price * company_commission_rate

    # اجمالي عمولة الشركة بدون ضرائب (القيمة الكلية من الشركة للعمولة)
    total_company_commission_before_tax = company_commission_amount

    # اجمالي الحافز المسلم للسلز (القيمة الكلية من الشركة للحافز)
    salesperson_incentive_amount = unit_price * salesperson_incentive_rate
    total_salesperson_incentive_paid = salesperson_incentive_amount

    # اجمالي المبلغ المسلم للشركة بعد 5% (القيمة الكلية من الشركة بعد 5℅)
    # This seems to be related to sales_tax_rate, assuming it\'s company_commission_amount * (1 - sales_tax_rate)
    # However, the prompt mentions
    total_company_income_after_5_percent = company_commission_amount * (Decimal("1") - sales_tax_rate)

    # ضرائب المبيعات والقيمة المضافة
    vat_amount = company_commission_amount * vat_rate
    sales_tax_amount = company_commission_amount * sales_tax_rate
    total_vat_and_sales_tax_amount = vat_amount + sales_tax_amount # اجمالي ضريبة 19% (من المبلغ الكلي)
    net_company_income_after_sales_tax = company_commission_amount - sales_tax_amount # اجمالي صافي مبلغ الشركة (بعد ضريبة المبيعات فقط)

    # عمولة السيلز
    salesperson_commission_amount = unit_price * salesperson_commission_rate
    total_salesperson_income_before_tax = salesperson_commission_amount + salesperson_incentive_amount # اجمالي المبلغ المستحق للسلز (قبل الضريبة)
    salesperson_tax_rate_decimal = salesperson_tax_rate / Decimal('100') if salesperson_tax_rate > 0 else Decimal('0')
    salesperson_tax_amount = total_salesperson_income_before_tax * salesperson_tax_rate_decimal # اجمالي الضريبة 19% على السلز (ضريبة السلز)
    net_salesperson_income = total_salesperson_income_before_tax - salesperson_tax_amount # اجمالي المبلغ المسلم للسيلز (بعد الضريبة)

    # عمولة مدير المبيعات
    sales_manager_commission_amount = company_commission_amount * sales_manager_commission_rate # Assuming sales_manager_commission_rate is a direct rate on company commission
    total_sales_manager_income_before_tax = sales_manager_commission_amount # اجمالي المبلغ المستحق لمدير المبيعات
    sales_manager_tax_rate_decimal = sales_manager_tax_rate / Decimal('100') if sales_manager_tax_rate > 0 else Decimal('0')
    sales_manager_tax_amount = sales_manager_commission_amount * sales_manager_tax_rate_decimal # اجمالي الضريبة 19% على مدير المبيعات
    net_sales_manager_income = sales_manager_commission_amount - sales_manager_tax_amount # اجمالي المبلغ المسلم لمدير المبيعات

    # الضريبة السنوية
    annual_tax_amount = company_commission_amount * annual_tax_rate
    net_company_income_after_all_taxes_and_commissions = company_commission_amount - vat_amount - sales_tax_amount - annual_tax_amount - total_sales_manager_income_before_tax # اجمالي صافي مبلغ الشركة (بعد الضرائب وعمولة الوسيط)

    # صافي دخل الشركة بعد كل الضرائب وعمولة السيلز
    final_company_income = net_company_income_after_all_taxes_and_commissions - total_salesperson_incentive_paid # اجمالي صافي مبلغ الشركة المتاح (بعد الضريبة السنوية + الحافز)

    return {
        "company_commission_amount": company_commission_amount,
        "total_company_commission_before_tax": total_company_commission_before_tax,
        "total_salesperson_incentive_paid": total_salesperson_incentive_paid,
        "total_company_income_after_5_percent": total_company_income_after_5_percent,
        "vat_amount": vat_amount,
        "sales_tax_amount": sales_tax_amount,
        "total_vat_and_sales_tax_amount": total_vat_and_sales_tax_amount,
        "net_company_income_after_sales_tax": net_company_income_after_sales_tax,
        "salesperson_commission_amount": salesperson_commission_amount,
        "total_salesperson_income_before_tax": total_salesperson_income_before_tax,
        "salesperson_tax_amount": salesperson_tax_amount,
        "net_salesperson_income": net_salesperson_income,
        "sales_manager_commission_amount": sales_manager_commission_amount,
        "total_sales_manager_income_before_tax": total_sales_manager_income_before_tax,
        "sales_manager_tax_amount": sales_manager_tax_amount,
        "net_sales_manager_income": net_sales_manager_income,
        "annual_tax_amount": annual_tax_amount,
        "net_company_income_after_all_taxes_and_commissions": net_company_income_after_all_taxes_and_commissions,
        "final_company_income": final_company_income,
    }

