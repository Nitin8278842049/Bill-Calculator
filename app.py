import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS STYLING (Escaped Curly Braces) ---------------- #
st.markdown(f"""
<style>
.main-container {{ border: 2px solid #005aa2; padding: 20px; border-radius: 8px; }}
.stApp {{ background-color: white; }}
.logo-container {{ text-align: center; margin-bottom: 5px; }}
.logo-container img {{ max-width: 160px; }}
.title {{ text-align: center; color: #005aa2; font-size: 28px; font-weight: 800; }}
.subtitle {{ text-align: center; color: #555; font-size: 14px; margin-bottom: 15px; }}
.card {{ background: white; padding: 18px; border-radius: 6px; border: 1px solid #dcdcdc; margin-bottom: 15px; }}
.section-res {{ background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 10px; border: 1px solid #d0e7ff; }}
.section-comm {{ background: #fff3e0; padding: 8px; border-radius: 4px; font-weight: 700; color: #e65100; margin-top: 10px; border: 1px solid #ffe0b2; }}
.row {{ display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; border-bottom: none; }}
.calc {{ font-size: 12px; color: #666; margin-left: 10px; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid #eee; }}
.total {{ font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; color: #d32f2f; }}
.green {{ color: #1a7f37; font-weight: 600; }}
.penalty {{ color: #d32f2f; font-weight: 700; background-color: #ffebee; border: 1px solid #ffcdd2; }}
div.stButton > button {{ background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }}
label {{ font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container"><img src="data:image/png;base64,{logo_base64}"></div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Residential & Commercial Detailed Analysis</div>
""", unsafe_allow_html=True)

# ---------------- INPUT CARD ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)
category = st.radio("Select Category", ["Residential", "Commercial"], horizontal=True)
network = st.selectbox("Network Type", ["Direct (Tata Power Network)", "Welcome (AEML Network)"])
mu_text = st.text_input("Metered Units (MU)", value="0")
load_text = st.text_input("Sanctioned Load (kW)", value="0")

if category == "Residential":
    su_text = st.text_input("Solar Units (BU)", value="0")
    rmd_text = "0"
else:
    rmd_text = st.text_input("Recorded Max Demand (RMD in kW)", value="0")
    su_text = "0"

calculate = st.button("Calculate Detailed Bill")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION LOGIC ---------------- #
if calculate:
    try:
        mu, su, load_kw, rmd = float(mu_text), float(su_text), float(load_text), float(rmd_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    is_welcome = "Welcome" in network
    bu = mu * 1.05785 if is_welcome else mu
    wheeling_rate = 2.93 if is_welcome else 2.76
    bu_math = f"{mu} × 1.05785 = {round(bu)} BU" if is_welcome else f"{round(bu)} BU"

    if category == "Residential":
        # Residential Slabs
        s1_u, s2_u, s3_u, s4_u = min(bu, 100), min(max(bu-100, 0), 200), min(max(bu-300, 0), 200), max(bu-500, 0)
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        total_energy = (s1_u*r1) + (s2_u*r2) + (s3_u*r3) + (s4_u*r4)
        fixed = 160.00
        add_fixed = 250 if load_kw > 10 else 0
        penalty = 0
        duty_pct, tose_rate, sec_style = 0.16, 0.3594, "section-res"
    else:
        # Commercial Slabs
        s1_u, s2_u = min(bu, 500), max(bu-500, 0)
        r1, r2 = 7.63, 9.42
        total_energy = (s1_u*r1) + (s2_u*r2)
        min_demand = load_kw * 0.75
        bmd = max(rmd, min_demand)
        fixed = bmd * 470.00
        penalty = (rmd - load_kw) * (470.00 * 1.5) if rmd > load_kw else 0
        add_fixed, duty_pct, tose_rate, sec_style = 0, 0.21, 0.1916, "section-comm"

    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50
    duty_base = max(total_energy + wheeling + fixed + add_fixed + penalty - solar_rebate, 0)
    duty = duty_base * duty_pct
    tose = bu * tose_rate
    final_total = duty_base + duty + tose

    # ---------------- DISPLAY RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Step 1
    st.markdown(f'<div class="{sec_style}">Step 1 : Unit & Demand Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation: {bu_math}</div>', unsafe_allow_html=True)
    if category == "Commercial":
        st.markdown(f'<div class="row"><span>Billing Demand (BMD)</span><span><b>{bmd:.2f} kW</b></span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation: Higher of RMD ({rmd}kW) or 75% Load ({min_demand:.2f}kW)</div>', unsafe_allow_html=True)

    # Step 2
    st.markdown(f'<div class="{sec_style}">Step 2 : Energy Charges</div>', unsafe_allow_html=True)
    if category == "Residential":
        for u, r, lbl in [(s1_u, r1, "0–100"), (s2_u, r2, "101–300"), (s3_u, r3, "301–500"), (s4_u, r4, "Above 500")]:
            if u > 0:
                st.markdown(f'<div class="row"><span>{lbl} Units (@ ₹{r})</span><span>₹{u*r:.2f}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="calc">Calculation: {round(u,2)} × {r} = ₹{u*r:.2f}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="row"><span>0–500 Units (@ ₹7.63)</span><span>₹{s1_u*r1:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation: {round(s1_u,2)} × 7.63 = ₹{s1_u*r1:.2f}</div>', unsafe_allow_html=True)
        if s2_u > 0:
            st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹9.42)</span><span>₹{s2_u*r2:.2f}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="calc">Calculation: {round(s2_u,2)} × 9.42 = ₹{s2_u*r2:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    # Step 3
    st.markdown(f'<div class="{sec_style}">Step 3 : Fixed & Statutory Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation: {mu} × {wheeling_rate} = ₹{wheeling:.2f}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="row"><span>{"Demand" if category == "Commercial" else "Fixed"} Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation: {"BMD " + str(bmd) + "kW × ₹470" if category == "Commercial" else "Standard Residential Rate"}</div>', unsafe_allow_html=True)

    if penalty > 0:
        st.markdown(f'<div class="row penalty"><span>Demand Penalty</span><span>₹{penalty:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation: Excess {rmd-load_kw:.2f}kW × ₹705 (150% rate)</div>', unsafe_allow_html=True)

    if su > 0:
        st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calc">Calculation: {su} × 0.50 = ₹{solar_rebate:.2f}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty ({int(duty_pct*100)}%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Tax on Sale (TOSE)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill: ₹{round(final_total):,}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
