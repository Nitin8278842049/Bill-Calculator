import streamlit as st
import base64

st.set_page_config(page_title="Mumbai Power Bill Calculator 2026", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS ---------------- #
st.markdown("""
<style>
.main-container { border: 2px solid #005aa2; padding: 20px; border-radius: 8px; }
.stApp { background-color: white; }
.logo-container { text-align: center; margin-bottom: 5px; }
.logo-container img { max-width: 160px; }
.title { text-align: center; color: #005aa2; font-size: 28px; font-weight: 800; }
.subtitle { text-align: center; color: #555; font-size: 14px; margin-bottom: 15px; }
.card { background: white; padding: 18px; border-radius: 6px; border: 1px solid #dcdcdc; margin-bottom: 15px; }
.section { background: #eef7ff; padding: 8px; border-radius: 4px; font-weight: 700; color: #005aa2; margin-top: 10px; border: 1px solid #d0e7ff; }
.row { display: flex; justify-content: space-between; padding: 8px; font-size: 14px; border: 1px solid #e6e6e6; margin-top: 4px; }
.calc { font-size: 12px; color: #666; margin-left: 6px; margin-bottom: 6px; }
.total { font-size: 22px; font-weight: 800; text-align: right; padding-top: 10px; }
.green { color: #1a7f37; font-weight: 600; }
.adani-text { color: #d73a49 !important; }
.adani-bg { background: #fff5f5 !important; border: 1px solid #ffccd0 !important; color: #d73a49 !important; }
div.stButton > button { background-color: #005aa2; color: white; font-size: 16px; font-weight: 700; height: 45px; width: 100%; }
label { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">MUMBAI POWER BILL CALCULATOR</div>
<div class="subtitle">Tariff Cycle 2025-26 | Tata & Adani Supply</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Select Network Type", 
    ["Welcome (AEML Network)", "Direct (Tata Power Network)", "Adani Direct Supply"])

mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Metered Units", value="0")
su_text = st.text_input("Solar Units (BU)", placeholder="Enter Solar Units", value="0")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Load", value="1")

calculate = st.button("Calculate Bill")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:
    try:
        mu = float(mu_text)
        su = float(su_text)
        load_kw = float(load_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    is_welcome = "Welcome" in network
    is_adani = "Adani" in network

    # Set Theme and Base Rates
    theme_class = "adani-bg" if is_adani else "section"
    tose_rate = 0.3594 # Universal for this update

    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        bu_calc = f"Calculation : BU = {mu} × 1.05785 = {round(bu)} BU"
    elif is_adani:
        bu = mu
        wheeling_rate = 2.93
        r1, r2, r3, r4 = 3.45, 6.70, 8.10, 9.05
        bu_calc = f"Calculation : BU = {round(bu)} BU"
    else: # Tata Direct
        bu = mu
        wheeling_rate = 2.76
        r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79
        bu_calc = f"Calculation : BU = {round(bu)} BU"

    if su > bu:
        st.error("Solar units cannot exceed BU.")
        st.stop()

    # -------- ENERGY SLABS --------
    s1_u = min(bu, 100)
    s2_u = min(max(bu - 100, 0), 200)
    s3_u = min(max(bu - 300, 0), 200)
    s4_u = max(bu - 500, 0)

    s1, s2, s3, s4 = s1_u * r1, s2_u * r2, s3_u * r3, s4_u * r4
    total_energy = s1 + s2 + s3 + s4

    # -------- PPCA SLAB CALCULATION --------
    # Slab rates: 0-100: 0.69, 101-300: 1.29, 301-500: 1.48, 500+: 1.57
    p1 = s1_u * 0.69
    p2 = s2_u * 1.29
    p3 = s3_u * 1.48
    p4 = s4_u * 1.57
    ppca_total = p1 + p2 + p3 + p4

    # Adani Special Floor Logic for low units (2-4 units)
    is_ppca_floor = False
    if is_adani and 0 < mu <= 4:
        ppca_total = 69.64
        is_ppca_floor = True

    # -------- FIXED & WHEELING --------
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50

    if bu <= 100: fixed = 90
    elif bu <= 500: fixed = 135
    else: fixed = 160

    additional_fixed = 250 if load_kw > 10 else 0

    # -------- TAXES --------
    # Duty is 16% on (Energy + Wheeling + Fixed + PPCA - Solar Rebate)
    duty_base = max(total_energy + wheeling + fixed + additional_fixed + ppca_total - solar_rebate, 0)
    duty = duty_base * 0.16
    tose = bu * tose_rate

    total = duty_base + duty + tose

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f'<div class="{theme_class}">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{theme_class}">Step 2 : Energy Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>0 – 100 Units (@ ₹{r1})</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>101 – 300 Units (@ ₹{r2})</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>301 – 500 Units (@ ₹{r3})</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹{r4})</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><strong>Total Energy Charges</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{theme_class}">Step 3 : Adjustments & Other Charges</div>', unsafe_allow_html=True)
    
    # PPCA Display
    ppca_note = " (Fixed Floor Applied)" if is_ppca_floor else " (Slab-wise)"
    st.markdown(f'<div class="row"><span>PPCA Charges{ppca_note}</span><span>₹{ppca_total:.2f}</span></div>', unsafe_allow_html=True)
    if not is_ppca_floor:
        st.markdown(f'<div class="calc">Rates: 0.69, 1.29, 1.48, 1.57 per slab</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges (@ ₹{wheeling_rate})</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed + additional_fixed:.2f}</span></div>', unsafe_allow_html=True)

    if su > 0:
        st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="{theme_class}">Step 4 : Government Taxes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE (@ ₹{tose_rate})</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    total_color = "#d73a49" if is_adani else "#005aa2"
    st.markdown(f'<div class="total" style="color:{total_color};">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
