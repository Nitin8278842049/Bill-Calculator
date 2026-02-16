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
.main-container {
    border: 2px solid #005aa2;
    padding: 20px;
    border-radius: 8px;
}
.stApp { background-color: white; }
.block-container { max-width: 760px; padding-top: 10px; }
.logo-container { text-align: center; margin-bottom: 5px; }
.logo-container img { max-width: 160px; }
.title {
    text-align: center;
    color: #005aa2;
    font-size: 28px;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #555;
    font-size: 14px;
    margin-bottom: 15px;
}
.card {
    background: white;
    padding: 18px;
    border-radius: 6px;
    border: 1px solid #dcdcdc;
    margin-bottom: 15px;
}
.section {
    background: #eef7ff;
    padding: 8px;
    border-radius: 4px;
    font-weight: 700;
    color: #005aa2;
    margin-top: 10px;
    border: 1px solid #d0e7ff;
}
.row {
    display: flex;
    justify-content: space-between;
    padding: 8px;
    font-size: 14px;
    border: 1px solid #e6e6e6;
    margin-top: 4px;
}
.calc {
    font-size: 12px;
    color: #666;
    margin-left: 6px;
    margin-bottom: 6px;
}
.total {
    font-size: 22px;
    font-weight: 800;
    color: black;
    text-align: right;
    padding-top: 10px;
}
div.stButton > button {
    background-color: #005aa2;
    color: white;
    font-size: 16px;
    font-weight: 700;
    border-radius: 4px;
    height: 45px;
    width: 100%;
    border: none;
}
label { font-weight: 600 !important; }
.green { color: #1a7f37; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

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
    ["Welcome (AEML Network)", "Direct (Tata Power Network)"]
)

mu_text = st.text_input("Metered Units (MU)", placeholder="Enter Meter Units")
solar_text = st.text_input("Solar Units (BU)", placeholder="Enter Solar Units")

calculate = st.button("Calculate")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATIONS ---------------- #
if calculate:

    try:
        mu = float(mu_text)
        solar_units = float(solar_text)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    if mu < 0 or solar_units < 0:
        st.error("Units cannot be negative.")
        st.stop()

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = mu * 1.0536
    else:
        bu = mu

    if solar_units > bu:
        st.error("Solar Units cannot exceed Billed Units.")
        st.stop()

    net_units = bu - solar_units

    # -------- SLABS ON NET UNITS --------
    s1_units = min(net_units, 100)
    s2_units = min(max(net_units - 100, 0), 200)
    s3_units = min(max(net_units - 300, 0), 200)
    s4_units = max(net_units - 500, 0)

    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79

    s1 = s1_units * r1
    s2 = s2_units * r2
    s3 = s3_units * r3
    s4 = s4_units * r4

    total_energy = s1 + s2 + s3 + s4

    wheeling = mu * 2.93
    fixed = 135  # matches mid slab case

    tose = net_units * 0.3594

    duty_base = total_energy + wheeling + fixed + tose
    duty = duty_base * 0.16

    total = total_energy + wheeling + fixed + tose + duty

    # ---------------- UI ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Units</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span><b>{round(bu)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : BU = {mu} × Loss Factor = {round(bu)}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Net Units</span><span><b>{round(net_units)}</b></span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="calc">Calculation : Net Units = {round(bu)} - {solar_units} = {round(net_units)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Energy Charges</span><span>₹{total_energy:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
