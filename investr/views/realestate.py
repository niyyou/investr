import streamlit as st
import pandas as pd
import altair as alt

from views.register import declare_view
import numpy as np
from box import Box


# monthly_infos = ["interests", "principal", "extra repayment", "loan balance"]


# @st.cache
# def aggregate_summary(df_summary, period_names, groupby_period):
#     global monthly_infos
#     grouped_df = df_summary.groupby(
#         [
#             df_summary.index.get_level_values(0),
#             (df_summary.index.get_level_values(1) - 1) // groupby_period,
#         ]
#     )
#     agg_func = zip(monthly_infos, ["sum", "sum", "sum", "min"])
#     grouped_df = grouped_df.agg(dict(agg_func))
#     grouped_df = grouped_df.reset_index()
#     grouped_df.month = grouped_df.month + 1
#     grouped_df = grouped_df.set_index(["year", "month"])
#     grouped_df.index.rename(("year", period_names[groupby_period]), inplace=True)
#     if groupby_period == 12:
#         grouped_df = grouped_df.droplevel(axis=0, level=1)
#     return grouped_df


def get_loan_summary(
    n_years,
    loan_total,
    interest_rate,
    monthly_payment,
    annual_extra_repayment_rate,
    **kwargs,
):
    loan_balance = loan_total
    data = []
    for y in range(1, int(n_years) + 1):
        annual_interests = loan_balance * interest_rate
        monthly_interests = annual_interests / 12
        monthly_principal = monthly_payment - monthly_interests
        annual_principal = monthly_principal * 12
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


@st.cache
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

    property_appreciation_rate = (
        st.number_input(
            "Property annual appreciation rate %", value=0, format="%d", step=1
        )
        / 100
    )

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


def make_sidebar(sidebar):
    with st.sidebar.expander("Property", True):
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

    with st.sidebar.expander("Acquisition cost", False):
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

    with st.sidebar.expander("Mortgage", True):
        sidebar.interest_rate = (
            st.number_input("Interest rate %", value=1.35, format="%.2f", step=0.01)
            / 100
        )
        sidebar.n_years = st.number_input(
            "Number of years", value=20, step=5, min_value=10, max_value=40
        )
        sidebar.monthly_payment = st.number_input(
            "Monthly payment", value=2600, step=100, min_value=100, max_value=5000
        )

        # Sonderntilgung
        sidebar.annual_extra_repayment_rate = (
            st.number_input(
                "Annual extra repayment %", value=0.0, format="%.1f", step=0.1
            )
            / 100
        )

    return sidebar


@declare_view("Real-estate")
def show_realestate(*args, **kwargs):

    sidebar = Box()
    sidebar = make_sidebar(sidebar)

    df_summary = get_loan_summary(**sidebar)
    loan_balance = df_summary.iloc[-1, -1]

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

                    Loan balance after **{int(sidebar.n_years)}** years: **{round(loan_balance):,}** €

                    Total paid interests: **{round(df_summary["annual_interests"].sum()):,}** €
                """
            )

    # period_names = {1: "month", 3: "trimester", 6: "semester", 12: "yearly"}

    with st.expander("Show table", expanded=False):
        st.table(df_summary.style.format("{:,.0f}"))

    df_summary_melt = (
        df_summary[["monthly_interests", "monthly_principal"]]
        .reset_index()[["year", "monthly_interests", "monthly_principal"]]
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
        .properties(width=800, height=200)
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
