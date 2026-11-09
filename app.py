# ============================================================
# Loan Payoff & Extra-Payment Calculator — a Streamlit web app
# Finance problem it solves: "How much interest and time do I save
# if I pay a little extra on my loan each month?"
# Run locally with:   streamlit run app.py
# ============================================================

# ---------- 1. IMPORTS ----------
import streamlit as st   # turns this Python script into a web app
import pandas as pd      # builds tables (DataFrames) for the schedule and chart


# ---------- 2. PAGE SETTINGS ----------
# Must be the first Streamlit command: sets the browser-tab title, icon and layout.
st.set_page_config(
    page_title="Loan Payoff Calculator",
    page_icon="💸",
    layout="centered",
)


# ---------- 3. FINANCE FUNCTIONS ----------
# The math lives in functions, separate from the interface, so it is easy to test.

def monthly_payment(principal, annual_rate_pct, years):
    """
    Standard amortized loan payment:
        M = P * r / (1 - (1 + r) ** -n)
    P = amount borrowed, r = monthly interest rate (decimal), n = number of monthly payments.
    """
    r = annual_rate_pct / 100 / 12   # e.g. 6% per year -> 0.005 per month
    n = years * 12                   # e.g. 30 years -> 360 payments
    if r == 0:                       # 0% loan: just split the principal evenly
        return principal / n         # (avoids dividing by zero in the formula)
    return principal * r / (1 - (1 + r) ** -n)


def amortization_schedule(principal, annual_rate_pct, years, extra=0.0):
    """
    Builds a month-by-month table showing how each payment is split
    between interest and principal, and what balance is left.
    `extra` is an optional additional amount paid toward principal each month.
    """
    r = annual_rate_pct / 100 / 12
    base_payment = monthly_payment(principal, annual_rate_pct, years)
    balance = principal
    rows = []
    month = 0

    # Keep paying until the balance is gone (with a safety cap of the full term).
    while balance > 0.005 and month < years * 12:
        month += 1
        interest = balance * r                          # interest charged this month
        payment = base_payment + extra                  # what you intend to pay
        payment = min(payment, balance + interest)      # last payment: don't overpay
        principal_paid = payment - interest             # the rest reduces the balance
        balance -= principal_paid
        rows.append({
            "Month": month,
            "Payment": payment,
            "Interest": interest,
            "Principal": principal_paid,
            "Balance": max(balance, 0.0),
        })

    return pd.DataFrame(rows)


def months_to_text(months):
    """Turns a number of months into readable text, e.g. 302 -> '25 yr 2 mo'."""
    yrs, mos = divmod(int(months), 12)
    return f"{yrs} yr {mos} mo"


# ---------- 4. HEADER ----------
st.title("💸 Loan Payoff & Extra-Payment Calculator")
st.write(
    "See your monthly payment, total interest, and how much time and money "
    "you save by paying a little extra each month. Works for student loans, "
    "car loans, and mortgages."
)
st.divider()


# ---------- 5. USER INPUTS ----------
# min_value / max_value block bad input (negatives, zero, absurd numbers)
# before it ever reaches the math. st.number_input only accepts numbers,
# so typing text like "hello" is rejected automatically.
col1, col2 = st.columns(2)

with col1:
    principal = st.number_input(
        "Loan amount ($)", min_value=100.0, max_value=10_000_000.0,
        value=25_000.0, step=1_000.0, format="%.2f",
    )
    years = st.number_input(
        "Loan term (years)", min_value=1, max_value=40, value=10, step=1,
    )

with col2:
    rate = st.number_input(
        "Annual interest rate (APR %)", min_value=0.0, max_value=36.0,
        value=6.5, step=0.25, format="%.2f",
    )
    extra = st.number_input(
        "Extra payment per month ($)", min_value=0.0, max_value=1_000_000.0,
        value=100.0, step=25.0, format="%.2f",
        help="Optional. Any amount above the required payment goes straight to principal.",
    )


# ---------- 6. RUN THE CALCULATIONS ----------
payment = monthly_payment(principal, rate, years)

# Two scenarios: paying only the minimum vs. paying the minimum + extra.
base = amortization_schedule(principal, rate, years, extra=0.0)
fast = amortization_schedule(principal, rate, years, extra=extra)

base_interest = base["Interest"].sum()
fast_interest = fast["Interest"].sum()
interest_saved = base_interest - fast_interest
months_saved = len(base) - len(fast)


# ---------- 7. RESULTS: STANDARD LOAN ----------
st.divider()
st.subheader("Your loan")

m1, m2, m3 = st.columns(3)
m1.metric("Monthly payment", f"${payment:,.2f}")
m2.metric("Total interest", f"${base_interest:,.2f}")
m3.metric("Total paid", f"${principal + base_interest:,.2f}")


# ---------- 8. RESULTS: WITH EXTRA PAYMENT ----------
if extra > 0:
    st.subheader(f"Paying ${extra:,.2f} extra each month")
    e1, e2, e3 = st.columns(3)
    e1.metric("Paid off in", months_to_text(len(fast)),
              delta=f"-{months_to_text(months_saved)}", delta_color="inverse")
    e2.metric("Total interest", f"${fast_interest:,.2f}",
              delta=f"-${interest_saved:,.2f}", delta_color="inverse")
    e3.metric("Interest saved", f"${interest_saved:,.2f}")

    st.success(
        f"Paying an extra **${extra:,.2f}/month** saves you **${interest_saved:,.2f}** "
        f"in interest and gets you debt-free **{months_to_text(months_saved)}** sooner."
    )
else:
    st.info("Tip: enter an extra monthly payment above to see how much you could save.")


# ---------- 9. CHART: BALANCE OVER TIME ----------
st.subheader("Remaining balance over time")

# Line the two scenarios up month by month in one table so Streamlit can chart both lines.
chart_data = pd.DataFrame({"Month": base["Month"], "Minimum payment only": base["Balance"]})
if extra > 0:
    chart_data = chart_data.merge(
        fast[["Month", "Balance"]].rename(columns={"Balance": "With extra payment"}),
        on="Month", how="left",
    ).fillna(0.0)   # after the faster loan is paid off, its balance stays at $0

st.line_chart(chart_data, x="Month", y_label="Balance ($)")


# ---------- 10. FORMULA USED ----------
st.subheader("Formula used")
st.latex(r"M = P \cdot \frac{r}{1 - (1 + r)^{-n}}")
st.markdown(
    "- **M** = monthly payment  \n"
    "- **P** = loan amount  \n"
    "- **r** = monthly interest rate = APR ÷ 12 ÷ 100  \n"
    "- **n** = number of payments = years × 12"
)

r = rate / 100 / 12
n = years * 12
if r > 0:
    st.latex(
        rf"M = {principal:,.2f} \cdot \frac{{{r:.6f}}}{{1 - (1 + {r:.6f})^{{-{n}}}}} = {payment:,.2f}"
    )
else:
    st.latex(rf"r = 0 \;\Rightarrow\; M = \frac{{P}}{{n}} = \frac{{{principal:,.2f}}}{{{n}}} = {payment:,.2f}")

st.caption(
    "Each month: interest = remaining balance × r. "
    "The rest of the payment (plus any extra) reduces the balance."
)


# ---------- 11. FULL AMORTIZATION SCHEDULE ----------
# An expander keeps the long table hidden until the user wants it.
schedule = fast if extra > 0 else base
with st.expander("📋 See the full month-by-month schedule"):
    st.dataframe(
        schedule.style.format({
            "Payment": "${:,.2f}", "Interest": "${:,.2f}",
            "Principal": "${:,.2f}", "Balance": "${:,.2f}",
        }),
        hide_index=True,
        width="stretch",   # table fills the full page width
    )
    # Let the user download the schedule as a CSV file to open in Excel.
    st.download_button(
        "⬇️ Download schedule (CSV)",
        data=schedule.round(2).to_csv(index=False),
        file_name="amortization_schedule.csv",
        mime="text/csv",
    )


# ---------- 12. FOOTER ----------
st.divider()
st.caption(
    "Educational tool built with Python & Streamlit. Assumes a fixed rate and monthly "
    "compounding; real loans may include fees or other terms. Not financial advice."
)
