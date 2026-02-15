import streamlit as st

st.set_page_config(page_title="Tata Power Bill Calculator", layout="centered")

st.title("⚡ TATA POWER BILL CALCULATOR")
st.caption("Mumbai Region Official Tariff")

# ---------------- INPUTS ---------------- #

network = st.selectbox(
    "Network Type",
    ["Welcome (AEML Network)", "Direct (Tata Power Network)"]
)

mu = st.number_input("Metered Units (MU)", min_value=0.0, step=1.0)
su = st.number_input("Solar Hour Units", min_value=0.0, step=1.0)

calculate = st.button("Calculate Bill")

# ---------------- CALCULATION ---------------- #

if calculate:

    is_welcome = "Welcome" in network

    # BU Calculation
    if is_welcome:
        bu = round(mu * 1.0536)
        note_bu = f"{mu} MU × 1.0536 = {bu} BU"
    else:
        bu = mu
        note_bu = f"Direct Network: BU = MU = {mu}"

    # Energy Slabs
    s1 = min(bu, 100) * 2.00
    s2 = min(max(bu - 100, 0), 200) * 5.20
    s3 = min(max(bu - 300, 0), 200) * 10.79
    s4 = max(bu - 500, 0) * 11.79

    total_energy = s1 + s2 + s3 + s4

    # Wheeling
    wheeling = mu * 2.93

    # Solar rebate
    solar_rebate = su * 0.50

    # Fixed Charges
    if bu > 500:
        fixed = 160
    elif bu > 100:
        fixed = 135
    else:
        fixed = 90

    # Duty
    duty_base = total_energy + wheeling + fixed - solar_rebate
    duty = duty_base * 0.16

    # TOSE
    tose = bu * 0.3594

    # Total
    total = total_energy + wheeling + fixed + duty + tose - solar_rebate

    # ---------------- DISPLAY ---------------- #

    st.divider()
    st.subheader("Step 1: Unit Conversion")
    st.write(f"**Billed Units (BU): {bu}**")
    st.caption(note_bu)

    st.subheader("Step 2: Energy Charges")
    st.write(f"0-100 Slab : ₹{s1:.2f}")
    st.write(f"101-300 Slab : ₹{s2:.2f}")
    st.write(f"301-500 Slab : ₹{s3:.2f}")
    st.write(f"Above 500 Slab : ₹{s4:.2f}")
    st.write(f"**Total Energy: ₹{total_energy:.2f}**")

    st.subheader("Step 3: Other Charges")
    st.write(f"Wheeling Charges : ₹{wheeling:.2f}")
    st.write(f"Solar Rebate : -₹{solar_rebate:.2f}")
    st.write(f"Fixed Charges : ₹{fixed:.2f}")
    st.write(f"Electricity Duty (16%) : ₹{duty:.2f}")
    st.write(f"TOSE : ₹{tose:.2f}")

    st.success(f"Net Bill Amount : ₹{round(total):,}")
