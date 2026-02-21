import streamlit as st

# --- Configuration ---
st.set_page_config(page_title="Mumbai Bill Pro 2026", page_icon="⚡")

# --- UI Header ---
st.title("⚡ Mumbai Electricity Calculator (2025-26)")
st.markdown("""
This calculator uses the **MERC 5th Control Period (FY 2025-26)** tariff orders. 
*Updated: February 2026*
""")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Billing Details")
    provider = st.selectbox("Utility Provider", ["Adani Electricity", "Tata Power (Direct)"])
    units = st.number_input("Monthly Units (kWh)", min_value=0, value=250, step=10)
    phase = st.radio("Connection Type", ["Single Phase", "Three Phase"])
    # Monthly variable: PPCA (Fuel adjustment)
    ppca_rate = st.slider("Current PPCA (₹/unit)", 0.0, 2.0, 0.45, help="Check your latest bill for the month's PPCA rate.")

# --- Data Store (Sourced from Case No 210 & 211 of 2024) ---
# Rates effective April 1, 2025 - March 31, 2026
TARIFF_DATA = {
    "Adani Electricity": {
        "slabs": [(100, 3.45), (300, 6.70), (500, 8.10), (float('inf'), 9.05)],
        "wheeling": 2.93,
        "fixed_single": {100: 90, 300: 135, 500: 135, 1000: 160},
        "fixed_three": 160,
        "tax_on_sale": 0.2604
    },
    "Tata Power (Direct)": {
        "slabs": [(100, 2.02), (300, 5.35), (500, 10.04), (float('inf'), 11.25)],
        "wheeling": 1.82,
        "fixed_single": {100: 90, 300: 135, 500: 135, 1000: 160},
        "fixed_three": 160,
        "tax_on_sale": 0.2604
    }
}

# --- Calculation Engine ---
def run_calculation(units, provider, phase, ppca):
    data = TARIFF_DATA[provider]
    
    # 1. Fixed Charges
    if phase == "Three Phase":
        fixed = data["fixed_three"]
    else:
        if units <= 100: fixed = data["fixed_single"][100]
        elif units <= 500: fixed = data["fixed_single"][300]
        else: fixed = data["fixed_single"][1000]

    # 2. Energy Charges (Slab Logic)
    energy_total = 0
    rem_units = units
    prev_limit = 0
    slab_breakdown = []
    
    for limit, rate in data["slabs"]:
        if rem_units > 0:
            units_in_slab = min(rem_units, limit - prev_limit)
            cost = units_in_slab * rate
            energy_total += cost
            slab_breakdown.append({"Slab": f"{prev_limit}-{limit if limit != float('inf') else '+'}", "Units": units_in_slab, "Rate": rate, "Cost": cost})
            rem_units -= units_in_slab
            prev_limit = limit

    # 3. Wheeling & PPCA
    wheeling = units * data["wheeling"]
    ppca_total = units * ppca
    
    # 4. Regulatory Taxes
    v_subtotal = fixed + energy_total + wheeling + ppca_total
    elec_duty = v_subtotal * 0.16  # 16% for Residential
    tax_on_sale = units * data["tax_on_sale"]
    
    total = v_subtotal + elec_duty + tax_on_sale
    
    return {
        "Fixed": fixed, "Energy": energy_total, "Wheeling": wheeling,
        "PPCA": ppca_total, "Duty": elec_duty, "TaxSale": tax_on_sale,
        "Total": total, "Slabs": slab_breakdown
    }

# --- Display Results ---
res = run_calculation(units, provider, phase, ppca_rate)

# Top Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Total Bill", f"₹{res['Total']:,.2f}")
c2.metric("Avg Rate/Unit", f"₹{res['Total']/max(units,1):.2f}")
c3.metric("Tax %", "16% + ToS")

# Detailed Table
st.subheader("Calculation Breakdown")
with st.expander("View Slab-wise Energy Details"):
    st.table(res["Slabs"])

st.markdown(f"""
| Component | Amount (INR) |
| :--- | :--- |
| **Fixed/Demand Charges** | ₹{res['Fixed']:.2f} |
| **Energy Charges (Base)** | ₹{res['Energy']:.2f} |
| **Wheeling Charges** | ₹{res['Wheeling']:.2f} |
| **PPCA (Fuel Adjustment)** | ₹{res['PPCA']:.2f} |
| **Electricity Duty (16%)** | ₹{res['Duty']:.2f} |
| **Tax on Sale** | ₹{res['TaxSale']:.2f} |
| **Grand Total** | **₹{res['Total']:,.2f}** |
""")

st.warning("**Note:** Adani rates for 301-500 units have increased slightly in the 2026 cycle to ₹8.10. Ensure your consumption is optimized!")
