import streamlit as st
import pandas as pd
import altair as alt

from views.register import declare_view
import numpy as np
from box import Box


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


def make_section_property(sidebar, prefix=""):
    with st.sidebar.expander(prefix + "Property", False):
        sidebar.plot_value = st.number_input(
            "Plot value",
            value=500_000,
            step=1_000,
        )

        sidebar.house_value = st.number_input(
            "Flat/house value",
            value=596_600 + 15_000,  # 611_600
            step=1_000,
        )

        sidebar.extra_house_cost = st.number_input(
            "Extra house costs",
            value=45_100 + 7500,
            step=1000,
        )

        sidebar.property_value = (
            sidebar.plot_value + sidebar.house_value + sidebar.extra_house_cost
        )

        sidebar.downpayment = st.number_input(
            "Downpayment",
            value=140_000,
            step=1_000,
        )

        sidebar.plot_surface = st.number_input("Plot surface (m\u00b2)", value=271.00)
        sidebar.living_space = st.number_input("Living space (m\u00b2)", value=128.24)
        sidebar.usable_space = st.number_input("Living space (m\u00b2)", value=152.52)
    return sidebar


def make_section_acquisition_cost(sidebar, prefix=""):
    with st.sidebar.expander(prefix + "Acquisition cost", False):
        sidebar.real_estate_rate = (
            st.number_input("Real-estate %", value=3.57, format="%.2f", step=0.01) / 100
        )
        sidebar.property_transfer_tax_rate = (
            st.number_input(
                "Property-transfer tax %", value=3.5, format="%.2f", step=0.01
            )
            / 100
        )
        sidebar.notary_rate = (
            st.number_input("Notary %", value=2.0, format="%.2f", step=0.01) / 100
        )

        sidebar.extra_fees_total = sidebar.plot_value * (
            sidebar.real_estate_rate
            + sidebar.property_transfer_tax_rate
            + sidebar.notary_rate
        )

        sidebar.loan_total = (
            sidebar.property_value + sidebar.extra_fees_total - sidebar.downpayment
        )
        return sidebar


def make_section_mortgage(sidebar, amount, interest, n_years, monthly, prefix=""):
    with st.sidebar.expander(f"({prefix}) Mortgage", True):
        sidebar[prefix] = {}
        sidebar[prefix].loan_total = st.number_input(
            "Amount", value=amount, min_value=0, key=prefix + "amount"
        )
        sidebar[prefix].interest_rate = (
            st.number_input(
                "Interest rate %",
                value=interest,
                format="%.2f",
                step=0.01,
                key=prefix + "interest",
            )
            / 100
        )
        sidebar[prefix].n_years = st.number_input(
            "Number of years",
            value=n_years,
            step=5,
            min_value=10,
            max_value=40,
            key=prefix + "nyears",
        )
        sidebar[prefix].monthly_payment = st.number_input(
            "Monthly payment",
            value=monthly,
            key=prefix + "monthly",
        )

    return sidebar


def print_summary(sidebar):
    with st.expander("Summary", True):
        col_1, col_2, col_3 = st.columns(3)
        with col_1:

            loan_to_value = (
                round(
                    (
                        sidebar.property_value
                        - sidebar.downpayment
                        + sidebar.extra_fees_total
                    )
                    / sidebar.property_value,
                    2,
                )
                * 100
            )

            st.markdown(
                f"""
                    Total price: **{round(sidebar.property_value + sidebar.extra_fees_total):,}** €

                    - Price/m\u00b2 (living space): **{round(sidebar.property_value / sidebar.usable_space):,}** €
                    - Price/m\u00b2 (total): **{round(sidebar.property_value / sidebar.plot_surface):,}** €


                    Downpayment: **{round(sidebar.downpayment):,}** €

                    Low-to-value ratio: **{loan_to_value}** %
                """
            )
        with col_2:
            st.markdown(
                f"""
                    Acquisition cost: **{round(sidebar.extra_fees_total):,}** €

                    - Real-estate fees: **{round(sidebar.plot_value * sidebar.real_estate_rate):,}** €
                    - Tax transfer fees: **{round(sidebar.plot_value * sidebar.property_transfer_tax_rate):,}** €
                    - Notary fees: **{round(sidebar.plot_value * sidebar.notary_rate):,}** €
                """
            )
        with col_3:
            st.markdown(
                f"""
                    Contracted loan: **{round(sidebar.loan_total):,}** €

                    Loan balance after **{int(sidebar.n_years)}** years: **{round(sidebar.loan_balance):,}** €

                    Total paid interests: **{round(sidebar.total_interests):,}** €
                """
            )


@declare_view("Combined mortgages")
def show_combined_mortages(*args, **kwargs):

    sidebar = Box()
    mortgage_length_toggle = st.sidebar.radio(
        "Mortgage length", ["20 years", "15 years"]
    )
    interests_only_period = st.sidebar.number_input(
        "Interest only period (years)",
        value=2,
        min_value=0,
    )
    start_month = st.sidebar.number_input("Starting month", 1, 12, 1, 0)

    # sidebar = make_section_property(sidebar)
    # sidebar = make_section_acquisition_cost(sidebar)

    if mortgage_length_toggle == "20 years":
        sidebar = make_section_mortgage(
            sidebar,
            amount=708_000,
            interest=1.41,
            n_years=20,
            monthly=23930 / 12,
            prefix="VRBank",
        )
    elif mortgage_length_toggle == "15 years":
        sidebar = make_section_mortgage(
            sidebar,
            amount=708_000,
            interest=1.17,
            n_years=15,
            monthly=22302 / 12,
            prefix="VRBank",
        )

    sidebar = make_section_mortgage(
        sidebar,
        amount=160_000,
        interest=0.87,
        n_years=10,
        monthly=6512.04 / 12,
        prefix="KfW",
    )
    sidebar = make_section_mortgage(
        sidebar,
        amount=200_000,
        interest=0.20,
        n_years=10,
        monthly=4400.04 / 12,
        prefix="CO2",
    )

    # Mortgage 1
    df_summary_vr = get_loan_summary(
        start_month=start_month,
        interests_only_period=interests_only_period,
        **sidebar.VRBank,
    )

    df_summary_vr = df_summary_vr[
        ["monthly_interests", "monthly_principal", "loan balance"]
    ]
    df_summary_vr.rename(
        columns={
            "monthly_interests": "VR Interests",
            "monthly_principal": "VR Principal",
            "loan balance": "VR Balance",
        },
        inplace=True,
    )

    # Mortgage 2
    df_summary_kfw = get_loan_summary(
        start_month=start_month,
        interests_only_period=interests_only_period,
        **sidebar.KfW,
    )

    df_summary_kfw = df_summary_kfw[
        ["monthly_interests", "monthly_principal", "loan balance"]
    ]
    df_summary_kfw.rename(
        columns={
            "monthly_interests": "KfW Interests",
            "monthly_principal": "KfW Principal",
            "loan balance": "KfW Balance",
        },
        inplace=True,
    )

    # Mortgage 3
    df_summary_co2 = get_loan_summary(
        start_month=start_month,
        interests_only_period=interests_only_period,
        **sidebar.CO2,
    )

    df_summary_co2 = df_summary_co2[
        ["monthly_interests", "monthly_principal", "loan balance"]
    ]
    df_summary_co2.rename(
        columns={
            "monthly_interests": "CO2 Interests",
            "monthly_principal": "CO2 Principal",
            "loan balance": "CO2 Balance",
        },
        inplace=True,
    )

    df_summary = (
        df_summary_vr.join(df_summary_kfw, how="outer")
        .join(df_summary_co2, how="outer")
        .fillna(0.0)
    )

    df_summary["Total Interests"] = (
        df_summary["VR Interests"]
        + df_summary["KfW Interests"]
        + df_summary["CO2 Interests"]
    )
    df_summary["Total Principal"] = (
        df_summary["VR Principal"]
        + df_summary["KfW Principal"]
        + df_summary["CO2 Principal"]
    )
    df_summary["Total Balance"] = (
        df_summary["VR Balance"] + df_summary["KfW Balance"] + df_summary["CO2 Balance"]
    )
    # sidebar.loan_balance = df_summary_vr.iloc[-1, -1]
    # sidebar.total_interests = df_summary_vr["annual_interests"].sum()

    with st.expander("Show table", expanded=True):
        st.dataframe(df_summary.style.format("{:,.0f}"), width=1500)

    df_summary_melt = (
        df_summary[
            [
                "VR Interests",
                "VR Principal",
                "KfW Interests",
                "KfW Principal",
                "CO2 Interests",
                "CO2 Principal",
            ]
        ]
        .reset_index()
        .melt(["year"], var_name="repayment type", value_name="monthly amount")
    )

    st.altair_chart(
        alt.Chart(df_summary_melt)
        .mark_bar(cornerRadiusTopLeft=0, cornerRadiusTopRight=0)
        .encode(
            x="year:N",
            y="monthly amount:Q",
            color="repayment type:N",
            opacity=alt.value(0.9),
        )
        .properties(width=800, height=400)
        .configure_axis(grid=False)
        .configure_view(strokeWidth=0),
        use_container_width=True,
    )

    # trimester_agg_summary = (
    #     aggregate_summary(df_summary, period_names, 3)
    #     .reset_index()[["year", "trimester", "interests", "principal"]]
    #     .melt(["year", "trimester"], var_name="repayment type", value_name="amount")
    # )

    # st.altair_chart(
    #     alt.Chart(trimester_agg_summary)
    #     .transform_calculate(trimester="(datum.year - 1) * 4 + datum.trimester")
    #     .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
    #     .encode(
    #         x="trimester:N",
    #         y="amount:Q",
    #         color="repayment type:N",
    #         opacity=alt.value(0.9),
    #     )
    #     .properties(width=800, height=200)
    #     .configure_axis(grid=False)
    #     .configure_view(strokeWidth=0)
    # )
    st.stop()

    st.write("---")
    st.subheader("Return on investment vs renting")

    # yearly_cold_rent = 1000 * 12
    # rent_increase_rate = 0.02
    # yearly_maintenance_cost = 220 * 12
    # yearly_property_tax = 150

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        yearly_cold_rent = (
            st.number_input("Monthly cold rent", value=1000, step=50) * 12
        )
    with col2:
        rent_increase_rate = (
            st.number_input("Rent yearly increase rate %", value=2, format="%d", step=1)
            / 100
        )
    with col3:
        yearly_maintenance_cost = st.number_input(
            "Yearly maintenance cost", value=220 * 12
        )
    with col4:
        yearly_property_tax = st.number_input("Property yearly tax", value=150)

    st.write(
        "We assume the rent increases by",
        round(rent_increase_rate * 100),
        "% each year. The cold rest is at",
        round(yearly_cold_rent / 12),
        "€. The yearly maintenance costs are",
        yearly_maintenance_cost,
        "€, and the annual property tax is",
        yearly_property_tax,
        "€.",
    )

    yearly_agg_summary = aggregate_summary(df_summary, period_names, 12)

    df = get_roi(
        yearly_agg_summary,
        property_value,
        extra_fees_total,
        yearly_cold_rent,
        n_years,
        rent_increase_rate,
        yearly_maintenance_cost,
        yearly_property_tax,
        surface,
    )

    # TODO: This part needs refactoring

    with st.expander("show ROI yearly data"):
        st.write(df.set_index("year").style.format("{:,.0f}"))

    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=["year"], empty="none"
    )
    line = (
        alt.Chart(df)
        .mark_area(interpolate="basis", point=True)
        .encode(
            x="year:Q",
            y="networth:Q",
            color=alt.Color("variable:N", legend=None),
            opacity=alt.value(0.4),
        )
    )

    selectors = (
        line.mark_point()
        .encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
        .add_selection(nearest)
    )

    text = (
        line.mark_text(align="left", dx=5, dy=-45)
        .encode(
            text=alt.condition(nearest, "label:N", alt.value(" ")), opacity=alt.value(1)
        )
        .transform_calculate(label='format(round(datum.networth), ",") + "€"')
    )
    # ).transform_calculate(label='format(datum.value, ",").replace(",", " ") + "€"')
    # ).transform_calculate(label='format(datum.value, ",") + "€"')

    rules = (
        alt.Chart(df)
        .mark_rule(color="gray")
        .encode(x="year:Q")
        .transform_filter(nearest)
    )

    equilib_mark = (
        alt.Chart(pd.DataFrame({"networth": [0]}))
        .mark_rule(strokeDash=[5, 5])
        .encode(y="networth:Q")
    )

    # other_info_interests = alt.Chart(df).mark_line().encode(
    #     x="year:Q",
    #     y="interests:Q",
    #     opacity=alt.value(0.5)
    # )
    # other_info_rent = alt.Chart(df).mark_line().encode(
    #     x="year:Q",
    #     y="rent:Q",
    #     opacity=alt.value(0.5)
    # )

    chart = alt.layer(line, selectors, rules, text, equilib_mark).properties(
        width=700, height=500
    )

    property_value_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x="year:Q",
            y="property:Q",
            tooltip=["label:N", "m2 price:Q"],
        )
        .transform_calculate(label='format(round(datum.property), ",") + "€"')
        .properties(width=700, height=200)
    )

    combined_chart = chart  # + property_value_chart
    combined_chart.configure_axis(grid=False).configure_view(strokeWidth=0)
    combined_chart

    property_value_chart

    with st.expander("Other charts", expanded=False):
        keep_cols = ["year", "property share", "interests", "rent", "extra costs"]
        df_other = df.loc[:, keep_cols].melt(
            id_vars=["year"], value_vars=keep_cols.remove("year")
        )

        other_charts = (
            (
                alt.Chart(df_other)
                .mark_line(interpolate="basis", point=False)
                .encode(
                    x="year:Q",
                    y="value:Q",
                    color=alt.Color("variable:N"),
                    opacity=alt.value(0.4),
                )
            )
            .properties(width=700, height=400)
            .interactive()
        )
        other_charts
        # keep = ["year", "amount invested", "property share", "interests", "rent", "extra costs", "networth", "property", "m2 price"]

    # line = alt.Chart(df).mark_line(interpolate='basis', point=True).encode(
    #     x='year:Q',
    #     y='value:Q',
    #     color='variable:N',
    #     tooltip=['value'],
    # )
    # st.altair_chart(line)

    # st.write('---')
    # st.subheader("Exploration")
