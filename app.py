import streamlit as st

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

# ---------------- CSS DESIGN ---------------- #
st.markdown("""
<style>

.main {
    background-color: #f0f2f5;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 750px;
}

/* Header */
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

/* Card */
.card{
    background:white;
    padding:25px;
    border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

/* Section header */
.section{
    background:#eef7ff;
    padding:12px 15px;
    border-radius:8px 8px 0 0;
    color:#005aa2;
    font-weight:700;
    margin-top:20px;
}

/* Result rows */
.row{
    display:flex;
    justify-content:space-between;
    padding:10px 5px;
    border-bottom:1px solid #eee;
    font-size:15px;
}

/* Total */
.total{
    background:#fff4f4;
    padding:15px;
    border-radius:8px;
    font-size:22px;
    font-weight:700;
    color:#d9534f;
    text-align:right;
}

/* Button */
div.stButton > button {
    background-color:#005aa2;
    color:white;
    font-size:18px;
    font-weight:600;
    border-radius:8px;
    height:50px;
    width:100%;
}
div.stButton > button:hover {
    background-color:#00447a;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="title">TATA POWER BILL CALCULATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Mumbai Region Official Tariff</div>', unsafe_allow_html=True)

# ---------------- INPUT CARD ---------------- #
st.markdown('<div class="card">', unsafe_allow_html=True)

network = st.selectbox(
    "Network Type",
    ["Welcome (AEML Network)", "Direct (Tata Power Network)"]
)

mu = st.number_input("Metered Units (Total MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Hour Units (Direct Meter Reading)", min_value=0.0, step=1.0)

calculate = st.button("Calculate & Show Logic")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CALCULATION ---------------- #
if calculate:

    is_welcome = "Welcome" in network

    if is_welcome:
        bu = round(mu * 1.0536)
        note_bu = f"Calculation: {mu} MU × 1.0536 (Wheeling Loss) = {bu} BU"
    else:
        bu = mu
        note_bu = f"Direct Network: BU = MU = {mu}"

    s1 = min(bu, 100) * 2.00
    s2 = min(max(bu - 100, 0), 200) * 5.20
    s3 = min(max(bu - 300, 0), 200) * 10.79
    s4 = max(bu - 500, 0) * 11.79
    total_energy = s1 + s2 + s3 + s4

    wheeling = mu * 2.93
    solar_rebate = su * 0.50

    if bu > 500:
        fixed = 160
    elif bu > 100:
        fixed = 135
    else:
        fixed = 90

    duty_base = total_energy + wheeling + fixed - solar_rebate
    duty = duty_base * 0.16
    tose = bu * 0.3594

    total = total_energy + wheeling + fixed + duty + tose - solar_rebate

    # ---------------- RESULT CARD ---------------- #
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 1: Unit Conversion</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Billed Units (BU)</span><span>{bu}</span></div>', unsafe_allow_html=True)
    st.caption(note_bu)

    st.markdown('<div class="section">Step 2: Energy Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>0 - 100 Slab</span><span>₹{s1:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>101 - 300 Slab</span><span>₹{s2:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>301 - 500 Slab</span><span>₹{s3:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Above 500 Slab</span><span>₹{s4:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><strong>Total Energy</strong><strong>₹{total_energy:.2f}</strong></div>', unsafe_allow_html=True)

    st.markdown('<div class="section">Step 3: Other Charges</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Wheeling Charges</span><span>₹{wheeling:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Solar Rebate</span><span>-₹{solar_rebate:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Fixed Charges</span><span>₹{fixed:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>Electricity Duty (16%)</span><span>₹{duty:.2f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="row"><span>TOSE</span><span>₹{tose:.2f}</span></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="total">Net Bill Amount : ₹{round(total):,}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
