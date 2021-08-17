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


def get_roi(
    yearly_agg_summary,
    property_value,
    first_fee,
    yearly_cold_rent,
    n_years,
    rent_increase_rate,
    yearly_maintenance_cost,
    yearly_property_tax,
    surface,
    property_appreciation_rate,
):
    interests = 0
    networth = -first_fee
    rent = 0
    property_share = 0
    extra_costs = 0
    property_value_ = property_value

    info_dict = {
        "year": [],
        "amount invested": [],
        "property share": [],
        "interests": [],
        "rent": [],
        "extra costs": [],
        "networth": [],
        "property": [],
        "m2 price": [],
    }

    for y in range(1, n_years + 1):
        info_dict["year"].append(y)

        interests += yearly_agg_summary.loc[y, "interests"]
        info_dict["interests"].append(-interests)

        initial_share_value = property_value - yearly_agg_summary.loc[y, "loan balance"]
        new_share_value = (
            initial_share_value * (1 + property_appreciation_rate) ** y
        )  # exponential
        # new_share_value = initial_share_value * (1 + property_appreciation_rate * y)  # linear
        diff_share_value = new_share_value - initial_share_value
        info_dict["property share"].append(diff_share_value)
        info_dict["amount invested"].append(initial_share_value)

        rent += yearly_cold_rent * (1 + rent_increase_rate) ** (y - 1)
        info_dict["rent"].append(rent)

        extra_costs += yearly_maintenance_cost + yearly_property_tax
        info_dict["extra costs"].append(-extra_costs)

        networth = -first_fee + diff_share_value + rent - interests - extra_costs
        info_dict["networth"].append(networth)

        property_value_ += property_value * property_appreciation_rate  # linear
        # property_value_ *= (1 + property_appreciation_rate)**y  # exponential
        info_dict["property"].append(property_value_)
        info_dict["m2 price"].append(round(property_value_ / surface, 2))

    return pd.DataFrame(info_dict)
