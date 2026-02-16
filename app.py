import streamlit as st
import base64

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------- LOAD LOGO ----------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_of_bin_file("logo.png")

# ---------------- CSS DESIGN ---------------- #
st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 750px;
}

.logo-container{
    text-align:center;
    margin-top:30px;
    margin-bottom:10px;
}
.logo-container img{
    max-width:180px;
}

.title {
    text-align:center;
    color:#005aa2;
    font-weight:700;
    font-size:32px;
}
.subtitle{
    text-align:center;
    color:#444;
    margin-bottom:25px;
}

.card{
    background:white;
    padding:25px;
    border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

.section{
    background:#eef7ff;
    padding:12px 15px;
    border-radius:8px;
    color:#005aa2;
    font-weight:700;
    margin-top:20px;
}

.row{
    display:flex;
    justify-content:space-between;
    padding:10px 5px;
    border-bottom:1px solid #eee;
    font-size:15px;
}

.green{
    color:#1a7f37;
    font-weight:600;
}

.total{
    background:#f2f2f2;
    padding:16px;
    border-radius:8px;
    font-size:24px;
    font-weight:800;
    text-align:right;
}

div.stButton > button {
    background-color:#005aa2;
    color:white;
    font-size:18px;
    font-weight:600;
    border-radius:8px;
    height:50px;
    width:100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
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

mu = st.number_input("Metered Units (MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Units (SU)", min_value=0.0, step=1.0)

calculate = st.button("Calculate & Show Logic")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION ---------------- #
if calculate:

    if su > mu:
        st.error("Solar units cannot exceed Metered Units.")
        st.stop()

    is_welcome = "Welcome" in network

    # BU Conversion
    if is_welcome:
        bu = mu * 1.0536
        note_bu = f"{mu:.2f} MU × 1.0536 (Wheeling Loss) = {bu:.2f} BU"
    else:
        bu = mu
        note_bu = f"Direct Network → BU = {bu:.2f}"

    # Slab Units
    s1_units = min(bu, 100)
    s2_units = min(max(bu - 100, 0), 200)
    s3_units = min(max(bu - 300, 0), 200)
    s4_units = max(bu - 500, 0)

    # Tariff Rates
    r1, r2, r3, r4 = 2.00, 5.20, 10.79, 11.79

    # Slab Charges
    s1 = s1_units * r1
    s2 = s2_units * r2
    s3 = s3_units * r3
    s4 = s4_units * r4

    total_energy = s1 + s2 + s3 + s4

    # Other Charges
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

    st.markdown('<div class="section">Step 1: Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span>{bu:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(note_bu)

    st.markdown('<div class="section">Step 2: Energy Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>0 – 100 Units @ ₹{r1}</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s1_units:.2f} × {r1} = ₹{s1:.2f}")

    st.markdown(f'<div class="row"><span>100 – 300 Units @ ₹{r2}</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s2_units:.2f} × {r2} = ₹{s2:.2f}")

    st.markdown(f'<div class="row"><span>300 – 500 Units @ ₹{r3}</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s3_units:.2f} × {r3} = ₹{s3:.2f}")

    st.markdown(f'<div class="row"><span>Above 500 Units @ ₹{r4}</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.caption(f"{s4_units:.2f} × {r4} = ₹{s4:.2f}")

    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3: Other Charges</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row green"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
