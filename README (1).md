# 💸 Loan Payoff & Extra-Payment Calculator

A Streamlit web app that answers a common personal-finance question:
**"How much interest and time do I save if I pay extra on my loan each month?"**

## Features
- Calculates the monthly payment for any fixed-rate loan (student, auto, mortgage)
- Shows total interest and total amount paid
- Compares minimum-payment payoff vs. payoff with an extra monthly payment
- Chart of remaining balance over time for both scenarios
- Displays the amortization formula, with your numbers plugged in
- Full month-by-month amortization schedule, downloadable as CSV
- Input validation (no negative, zero, or text values)

## Formula
M = P · r / (1 − (1 + r)^−n), where r = APR ÷ 12 ÷ 100 and n = years × 12

## Verification (tested against known values)
| Input | Expected | App result | Status |
|---|---|---|---|
| $200,000, 6%, 30 yr | $1,199.10/mo, $231,676.38 interest | $1,199.10, $231,676.38 | ✓ PASS |
| $25,000, 6.5%, 10 yr | $283.87/mo | $283.87 | ✓ PASS |
| $12,000, 0%, 1 yr | $1,000.00/mo, $0 interest | $1,000.00, $0.00 | ✓ PASS |
| $1,000, 36%, 1 yr, $5,000 extra | Paid off in 1 month, $30 interest | 1 month, $30.00 | ✓ PASS |
| Negative / zero / text input | Blocked | Blocked by input limits | ✓ PASS |

## Built with
Python · Streamlit · pandas · AI-assisted coding
