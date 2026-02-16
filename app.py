import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS (Mobile Friendly) ---------------- #
st.markdown("""
<style>

/* Main Page Border */
.main-container {
    border: 2px solid #005aa2;
    padding: 14px;
    border-radius: 10px;
}

/* Mobile width optimization */
.block-container {
    max-width: 520px;
    padding-top: 5px;
}

/* Logo */
.logo-container {
    text-align: center;
    margin-bottom: 0px;
}
.logo-container img {
    max-width: 130px;
}

/* Titles */
.title {
    text-align: center;
    color: #005aa2;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    font-size: 12px;
    margin-bottom: 10px;
    color: #555;
}

/* Card */
.card {
    background: white;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #dcdcdc;
    margin-bottom: 10px;
}

/* Section Headers */
.section {
    background: #eef7ff;
    padding: 6px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 13px;
    color: #005aa2;
    margin-top: 8px;
    border: 1px solid #d0e7ff;
}

/* Rows */
.row {
    display: flex;
    justify-content: space-between;
    padding: 7px;
    font-size: 13px;
    border: 1px solid #e6e6e6;
    margin-top: 3px;
}

/* Calculation text */
.calc {
    font-size: 11px;
    color: #666;
    margin-left: 4px;
    margin-bottom: 4px;
}

/* Button */
div.stButton > button {
    background-color: #005aa2;
    color: white;
    font-size: 15px;
    font-weight: 700;
    border-radius: 6px;
    height: 42px;
    width: 100%;
    border: none;
}

/* Rebate */
.green {
    color: #1a7f37;
    font-weight: 600;
}

/* Net Bill */
.total {
    font-size: 18px;
    font-weight: 800;
    color: black;
    text-align: right;
    padding-top: 8px;
}

/* Reduce input spacing for mobile */
div[data-baseweb="input"] {
    margin-bottom: 6px;
}

label {
    font-weight: 600 !important;
    font-size: 13px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- PAGE ---------------- #
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Mumbai Region Official Tariff</div>
""", unsafe_allow_html=True)

# ---------------- INPUTS ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox(
    "Network Type",
    ["Welcome (AEML Network - 5.36% Loss)", "Direct (Tata Power Network)"]
)

mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Meter Units")
su_text = st.text_input("Solar Units", placeholder="Enter Solar Units")

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION ---------------- #
if calculate:

    try:
        mu = float(mu_text)
        su = float(su_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    if mu < 0 or su < 0:
        st.error("Units cannot be negative.")
        st.stop()

    if su > mu:
        st.error("Solar units cannot exceed Metered Units.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.0536
        bu_calc = f"Calculation: {mu} MU × 1.0536 (Wheeling Loss) = {round(bu)} BU"
    else:
        bu = mu
        bu_calc = f"Calculation: Direct Network → BU = {round(bu)}"

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

    wheeling = mu * 2.93
    solar_rebate = su * 0.50

    if bu <= 100:
        fixed = 90
    elif bu <= 500:
        fixed = 135
    else:
        fixed = 160

    duty_base = max(total_energy + wheeling + fixed - solar_rebate, 0)
    duty = duty_base * 0.16

    tose = bu * 0.3594

    total = total_energy + wheeling + fixed + duty + tose - solar_rebate

    # ---------------- RESULTS ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1 : Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 2 : Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0 – 100 Units (@ ₹2.00)</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{round(s1_units)} BU × ₹2.00</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>101 – 300 Units (@ ₹5.20)</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{round(s2_units)} BU × ₹5.20</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>301 – 500 Units (@ ₹10.79)</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{round(s3_units)} BU × ₹10.79</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Above 500 Units (@ ₹11.79)</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{round(s4_units)} BU × ₹11.79</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3 : Other Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{mu} MU × ₹2.93</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{su} MU × ₹0.50</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>TOSE (@ ₹0.3594 / BU)</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{round(bu)} BU × ₹0.3594</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
