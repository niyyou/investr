import streamlit as st
import pandas as pd
import altair as alt

from investr.common.mortgage import get_loan_summary
from investr.views.register import declare_view
from box import Box
from itertools import cycle


def make_section_property(sidebar, name=""):
    with st.sidebar.expander(name + "Property", False):
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


def make_section_acquisition_cost(sidebar, name=""):
    with st.sidebar.expander(name + "Acquisition cost", False):
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


def make_section_mortgage(sidebar, amount, interest, n_years, monthly, name=""):
    with st.sidebar.expander(f"{name}", False):
        sidebar[name] = {}
        sidebar[name].loan_total = st.number_input(
            "Amount", value=amount, min_value=0, key=name + "amount"
        )
        sidebar[name].interest_rate = (
            st.number_input(
                "Interest rate %",
                value=interest,
                format="%.2f",
                step=0.01,
                key=name + "interest",
            )
            / 100
        )
        sidebar[name].n_years = st.number_input(
            "Number of years",
            value=n_years,
            step=5,
            min_value=5,
            max_value=40,
            key=name + "nyears",
        )
        sidebar[name].monthly_payment = st.number_input(
            "Monthly payment",
            value=monthly,
            key=name + "monthly",
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
                    Total price: **{round(sidebar.property_value + sidebar.extra_fees_total):,}** ???

                    - Price/m\u00b2 (living space): **{round(sidebar.property_value / sidebar.usable_space):,}** ???
                    - Price/m\u00b2 (total): **{round(sidebar.property_value / sidebar.plot_surface):,}** ???


                    Downpayment: **{round(sidebar.downpayment):,}** ???

                    Low-to-value ratio: **{loan_to_value}** %
                """
            )
        with col_2:
            st.markdown(
                f"""
                    Acquisition cost: **{round(sidebar.extra_fees_total):,}** ???

                    - Real-estate fees: **{round(sidebar.plot_value * sidebar.real_estate_rate):,}** ???
                    - Tax transfer fees: **{round(sidebar.plot_value * sidebar.property_transfer_tax_rate):,}** ???
                    - Notary fees: **{round(sidebar.plot_value * sidebar.notary_rate):,}** ???
                """
            )
        with col_3:
            st.markdown(
                f"""
                    Contracted loan: **{round(sidebar.loan_total):,}** ???

                    Loan balance after **{int(sidebar.n_years)}** years: **{round(sidebar.loan_balance):,}** ???

                    Total paid interests: **{round(sidebar.total_interests):,}** ???
                """
            )


@declare_view("Combined mortgages")
def show_combined_mortages(*args, **kwargs):

    sidebar = Box()
    data = []

    with st.sidebar.expander("Basic inputs", expanded=True):
        interests_only_period = st.number_input(
            "Interest only period (years)",
            value=2,
            min_value=0,
        )
        free_period = st.number_input(
            "Free period (years)",
            value=1,
            min_value=0,
        )
        start_month = st.number_input(
            "Starting month", min_value=1, max_value=12, value=9, step=0
        )

        mortgage_config = st.file_uploader(
            "Upload a mortgage configuration", ["yml", "yaml"]
        )

        default_mortgage_data = [
            dict(
                amount=500_000,
                interest=1.00,
                n_years=10,
                monthly=2000,
                name="Mortgage {}",
            )
        ]

        if mortgage_config is not None:
            try:
                loaded_configuration = Box.from_yaml(mortgage_config)
                loaded_configuration = list(loaded_configuration.values())
            except:
                pass
            else:
                default_mortgage_data = loaded_configuration

    with st.sidebar.expander("Manual specification", expanded=True):
        n_mortgages = int(
            st.number_input(
                "Number of mortgages", min_value=1, value=len(default_mortgage_data)
            )
        )
        default_mortgage_names = cycle([m["name"] for m in default_mortgage_data])
        max_n_years = max([m["n_years"] for m in default_mortgage_data])

        default_mortgage_data = cycle(default_mortgage_data)

        mortgage_names = []
        for n in range(n_mortgages):
            mortgage_name = next(default_mortgage_names)
            mortgage_name = mortgage_name.format(n + 1)
            mortgage_names.append(
                st.text_input(
                    f"Mortgage #{n + 1} name",
                    value=mortgage_name,
                )
            )

    for n in range(n_mortgages):
        mortgage_data = next(default_mortgage_data)
        mortgage_data = mortgage_data.copy()
        _ = mortgage_data.pop("name").format(n + 1)
        sidebar = make_section_mortgage(
            sidebar, name=mortgage_names[n], **mortgage_data
        )

        df = get_loan_summary(
            start_month=start_month,
            interests_only_period=interests_only_period,
            free_period=free_period,
            **sidebar[mortgage_names[n]],
        )

        df = df[["monthly_interests", "monthly_principal", "loan balance"]]
        df.rename(
            columns={
                "monthly_interests": f"interests",
                "monthly_principal": f"principal",
                "loan balance": f"balance",
            },
            inplace=True,
        )
        df.columns = pd.MultiIndex.from_product([df.columns, [mortgage_names[n]]])
        data.append(df)

    df = data[0]
    if len(data) > 1:
        for i in range(1, len(data)):
            df = df.join(data[i], how="outer")

    df["balance"] = df["balance"].fillna(method="pad")
    df.fillna(value=0.0, inplace=True)

    df["interests", "total"] = df[["interests"]].groupby(level=0, axis=1).sum()
    df["principal", "total"] = df[["principal"]].groupby(level=0, axis=1).sum()
    df["balance", "total"] = df[["balance"]].groupby(level=0, axis=1).sum()

    st.markdown(
        f"""
        Loan balance after **{int(max_n_years)}** years: **{round(df['balance', 'total'].iloc[-1]):,}** ???

        Total paid interests: **{round(df['interests', 'total'].sum() * 12):,}** ???
        """
    )
    with st.expander("Show table", expanded=True):
        st.dataframe(
            df[["principal", "interests", "balance"]].style.format("{:,.0f}"),
            width=1500,
        )

    # st.write(df[["interests", "principal"]])
    # st.stop()

    df_plot = df[["interests", "principal"]].drop("total", axis=1, level=1)

    if st.checkbox("Breakdown data"):
        df_plot.columns = [f"{b} {a}" for a, b in df_plot.columns]

    df_melt = df_plot.reset_index().melt(
        ["year"], var_name="repayment type", value_name="monthly amount"
    )

    df_melt["monthly amount"] = df_melt["monthly amount"].apply(round)

    st.altair_chart(
        alt.Chart(df_melt)
        .mark_bar(cornerRadiusTopLeft=0, cornerRadiusTopRight=0)
        .transform_calculate(amount="datum['monthly amount'] + ' ???'")
        .encode(
            x="year:N",
            y="monthly amount:Q",
            color="repayment type:N",
            opacity=alt.value(0.9),
            tooltip=["repayment type", "amount:N"],
        )
        .properties(width=800, height=400)
        .configure_axis(grid=False)
        .configure_view(strokeWidth=0),
        use_container_width=True,
    )
