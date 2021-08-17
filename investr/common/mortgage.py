import pandas as pd


def get_loan_summary(
    n_years,
    loan_total,
    interest_rate,
    monthly_payment,
    annual_extra_repayment_rate=0,
    interests_only_period=0,
    start_month=1,
    **kwargs,
):
    loan_balance = loan_total
    data = []
    for y in range(1, int(n_years) + 1):
        n_months = 12 if y > 1 else 13 - start_month
        annual_interests = loan_balance * interest_rate * (n_months / 12)
        monthly_interests = annual_interests / n_months

        monthly_principal = 0
        annual_principal = 0
        annual_extra_repayment = 0
        if y > interests_only_period:
            monthly_principal = monthly_payment - monthly_interests
            annual_principal = monthly_principal * n_months
            loan_balance -= annual_principal
            annual_extra_repayment = loan_total * annual_extra_repayment_rate
            loan_balance -= annual_extra_repayment

        data.append(
            [
                y,
                monthly_interests,
                monthly_principal,
                annual_interests,
                annual_principal,
                annual_extra_repayment,
                loan_balance,
            ]
        )
    cols = [
        "year",
        "monthly_interests",
        "monthly_principal",
        "annual_interests",
        "annual_principal",
        "extra repayment",
        "loan balance",
    ]
    df = pd.DataFrame(data, columns=cols).set_index("year")
    return df
