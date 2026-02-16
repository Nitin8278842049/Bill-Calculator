import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- MINIMAL NEUTRAL CSS ---------------- #
st.markdown("""
<style>

/* Remove Streamlit default padding excess */
.block-container {
    max-width: 760px;
    padding-top: 10px;
}

/* Plain background */
.stApp {
    background-color: white;
}

/* Logo */
.logo-container {
    text-align: center;
    margin-top: 10px;
    margin-bottom: 10px;
}
.logo-container img {
    max-width: 200px;
    width: 100%;
    height: auto;
}

/* Titles */
.title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: black;
}
.subtitle {
    text-align: center;
    font-size: 14px;
    color: #555;
    margin-bottom: 20px;
}

/* Card */
.card {
    background: white;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 16px;
    border: 1px solid #dddddd;
}

/* Section headers */
.section {
    font-size: 15px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 6px;
}

/* Rows */
.row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    font-size: 14px;
    border-bottom: 1px solid #eeeeee;
}

/* Calculation logic text */
.calc {
    font-size: 12px;
    color: #666;
    margin-bottom: 6px;
}

/* Total */
.total {
    background: #f7f7f7;
    padding: 10px;
    border-radius: 4px;
    font-size: 20px;
    font-weight: 700;
    text-align: right;
    margin-top: 10px;
    border: 1px solid #dddddd;
}

/* Button */
div.stButton > button {
    background-color: white;
    color: black;
    font-size: 14px;
    font-weight: 600;
    border-radius: 4px;
    height: 42px;
    width: 100%;
    border: 1px solid #cccccc;
}

div.stButton > button:hover {
    background-color: #f5f5f5;
}

label {
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown(f"""
<div class="logo-container">
    <img src="data:image/png;base64,{logo_base64}">
</div>
<div class="title">TATA POWER BILL CALCULATOR</div>
<div class="subtitle">Tariff Calculation Logic</div>
""", unsafe_allow_html=True)

# ---------------- INPUT CARD ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox(
    "Network Type",
    ["Welcome (AEML Network)", "Direct (Tata Power Network)"]
)

mu = st.number_input("Metered Units (MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Units (SU)", min_value=0.0, step=1.0)

calculate = st.button("Calculate Bill")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:

    if su > mu:
        st.error("Solar units cannot exceed Metered Units.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.0536
        bu_calc = f"{mu:.2f} × 1.0536 = {bu:.2f} BU"
    else:
        bu = mu
        bu_calc = f"BU = {bu:.2f}"

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

    # ---------------- RESULT CARD ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{bu:.2f}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu_calc}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0 – 100 Units</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{s1_units:.2f} × {r1}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>100 – 300 Units</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{s2_units:.2f} × {r2}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>300 – 500 Units</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{s3_units:.2f} × {r3}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Above 500 Units</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{s4_units:.2f} × {r4}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Other Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{mu:.2f} × 2.93</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{su:.2f} × 0.50</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Electricity Duty</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{duty_base:.2f} × 16%</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">{bu:.2f} × 0.3594</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
