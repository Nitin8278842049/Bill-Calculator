import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

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
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Based Regional Tariff (Residential)</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox("Network Type", ["Welcome (AEML Network)", "Direct (Tata Power Network)"])
mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Metered Units")
su_text = st.text_input("Solar Units (BU)", placeholder="Enter Solar Units")
load_text = st.text_input("Sanctioned Load (kW)", placeholder="Enter Load")

calculate = st.button("Calculate")

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

    if is_welcome:
        bu = mu * 1.05785
        wheeling_rate = 2.93
    else:
        bu = mu
        wheeling_rate = 2.76

    if su > bu:
        st.error("Solar units cannot exceed Billed Units.")
        st.stop()

    # -------- SLABS --------
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79

    s1 = s1_units * r1
    s2 = s2_units * r2
    s3 = s3_units * r3
    s4 = s4_units * r4

    total_energy = s1 + s2 + s3 + s4

    # -------- PPCA --------
    pp1_rate, pp2_rate, pp3_rate, pp4_rate = 0.05, 0.10, 0.20, 0.25

    pp1 = s1_units * pp1_rate
    pp2 = s2_units * pp2_rate
    pp3 = s3_units * pp3_rate
    pp4 = s4_units * pp4_rate

    total_ppca = pp1 + pp2 + pp3 + pp4

    # -------- OTHER CHARGES --------
    wheeling = mu * wheeling_rate
    solar_rebate = su * 0.50

    if bu <= 100:
        fixed = 90
    elif bu <= 500:
        fixed = 135
    else:
        fixed = 160

    additional_fixed = 250 if load_kw > 10 else 0

    # -------- DUTY --------
    duty_base = max(total_energy + total_ppca + wheeling + fixed + additional_fixed - solar_rebate, 0)
    duty = duty_base * 0.16

    # -------- TOSE --------
    tose = bu * 0.3594

    # -------- FINAL TOTAL --------
    total = (
        total_energy
        + total_ppca
        + wheeling
        + fixed
        + additional_fixed
        + duty
        + tose
        - solar_rebate
    )

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Energy Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Total Energy Charges</span><span>₹{total_energy:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">PPCA Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Total PPCA</span><span>₹{total_ppca:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Other Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)

    if additional_fixed:
        st.markdown(f'<div class="row"><span>Additional Fixed Charges</span><span>₹{additional_fixed:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Tax on Sale of Electricity (TOSE)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
