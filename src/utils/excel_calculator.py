"""
Excel Calculation Logic Implementation
This module implements the exact calculation logic from the Excel file
"""

from decimal import Decimal, ROUND_HALF_UP

class ExcelCalculationEngine:
    """
    Implements the exact calculation logic from the Excel file
    """
    
    def __init__(self):
        # Default tax rates from Excel
        self.VAT_RATE = Decimal('0.14')  # 14% VAT
        self.SALES_TAX_RATE = Decimal('0.05')  # 5% Sales Tax
        self.ANNUAL_TAX_RATE = Decimal('0.225')  # 22.5% Annual Tax
        self.SALES_MANAGER_COMMISSION_RATE = Decimal('0.003')  # 0.3% Sales Manager Commission
        
    def calculate_sale_financials(self, unit_price, property_type_rates):
        """
        Calculate all financial aspects of a sale following Excel logic exactly
        
        Args:
            unit_price (Decimal): Unit price
            property_type_rates (dict): Property type rates containing commission rates
            
        Returns:
            dict: Complete financial breakdown
        """
        unit_price = Decimal(str(unit_price))
        
        # Extract rates from property type rates
        company_commission_rate = Decimal(str(property_type_rates.get('company_commission_rate', 0)))
        salesperson_commission_rate = Decimal(str(property_type_rates.get('salesperson_commission_rate', 0)))
        salesperson_incentive_rate = Decimal(str(property_type_rates.get('salesperson_incentive_rate', 0)))
        additional_incentive_tax_rate = Decimal(str(property_type_rates.get('additional_incentive_tax_rate', 0)))
        
        # Step 1: Company Commission Calculations (Following Excel C10, D10, E10, F10)
        company_commission_gross = unit_price * company_commission_rate
        
        # Step 2: Salesperson Incentive Calculations (Following Excel C11, D11, E11, F11)
        salesperson_incentive_total = unit_price * salesperson_incentive_rate
        
        # Step 3: Company Commission After VAT (Following Excel C14, D14, E14, F14)
        # Excel formula: =C10/1.14
        company_commission_after_vat = company_commission_gross / (Decimal('1') + self.VAT_RATE)
        
        # Step 4: VAT Amount (Following Excel C15, D15, E15, F15)
        # Excel formula: =C10-C14
        vat_amount = company_commission_gross - company_commission_after_vat
        
        # Step 5: Sales Tax Amount (Following Excel C16, D16, E16, F16)
        # Excel formula: =C14*K11 (where K11 is 5%)
        sales_tax_amount = company_commission_after_vat * self.SALES_TAX_RATE
        
        # Step 6: Total Tax 19% (Following Excel C17, D17, E17, F17)
        # Excel formula: =C15+C16
        total_tax_19_percent = vat_amount + sales_tax_amount
        
        # Step 7: Company Amount After Sales Tax (Following Excel C12, D12, E12, F12)
        # Excel formula: =C10-C16 (but we use after VAT amount minus sales tax)
        company_after_sales_tax = company_commission_after_vat - sales_tax_amount
        
        # Step 8: Company Net Before Annual Tax (Following Excel C18, D18, E18, F18)
        # Excel formula: =C10-C17
        company_net_before_annual = company_commission_gross - total_tax_19_percent
        
        # Step 9: Salesperson Commission Calculations
        salesperson_commission_total = unit_price * salesperson_commission_rate
        
        # Step 10: Additional Incentive Tax
        additional_incentive_tax = salesperson_incentive_total * additional_incentive_tax_rate
        
        # Step 11: Salesperson Tax (19% on commission - following Excel logic)
        salesperson_tax_19_percent = salesperson_commission_total * Decimal('0.19')
        
        # Step 12: Net Salesperson Amount
        salesperson_net_amount = salesperson_commission_total - salesperson_tax_19_percent
        
        # Step 13: Sales Manager Commission
        sales_manager_commission = unit_price * self.SALES_MANAGER_COMMISSION_RATE
        
        # Step 14: Company Net After All Deductions (Before Annual Tax)
        # Following Excel C24 logic: Company net - salesperson amounts - manager commission
        company_net_after_deductions = (company_net_before_annual - 
                                      salesperson_commission_total - 
                                      salesperson_incentive_total - 
                                      additional_incentive_tax - 
                                      sales_manager_commission)
        
        # Step 15: Annual Tax Amount (Following Excel C25)
        # Excel formula: =C24*K12 (where K12 is 22.5%)
        annual_tax_amount = company_net_after_deductions * self.ANNUAL_TAX_RATE
        
        # Step 16: Final Company Net Income (Following Excel C26, C27)
        # Excel formula: =C24-C25
        company_final_net_income = company_net_after_deductions - annual_tax_amount
        
        # Step 17: Company Available Amount (Same as final net in Excel)
        company_available_amount = company_final_net_income
        
        # Round all values to 2 decimal places
        def round_decimal(value):
            return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            # Company Commission Section
            'company_commission_gross': round_decimal(company_commission_gross),
            'company_commission_after_vat': round_decimal(company_commission_after_vat),
            'company_after_sales_tax': round_decimal(company_after_sales_tax),
            
            # Tax Section
            'vat_amount': round_decimal(vat_amount),
            'sales_tax_amount': round_decimal(sales_tax_amount),
            'total_tax_19_percent': round_decimal(total_tax_19_percent),
            'annual_tax_amount': round_decimal(annual_tax_amount),
            
            # Salesperson Section
            'salesperson_incentive_total': round_decimal(salesperson_incentive_total),
            'salesperson_commission_total': round_decimal(salesperson_commission_total),
            'salesperson_tax_19_percent': round_decimal(salesperson_tax_19_percent),
            'salesperson_net_amount': round_decimal(salesperson_net_amount),
            'additional_incentive_tax': round_decimal(additional_incentive_tax),
            
            # Management Section
            'sales_manager_commission': round_decimal(sales_manager_commission),
            
            # Final Results Section
            'company_net_before_annual': round_decimal(company_net_before_annual),
            'company_net_after_deductions': round_decimal(company_net_after_deductions),
            'company_final_net_income': round_decimal(company_final_net_income),
            'company_available_amount': round_decimal(company_available_amount),
            
            # Additional calculations for compatibility
            'net_company_income': round_decimal(company_final_net_income),  # For backward compatibility
        }

