from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Dashboard color palette
COLORS = {
    "background": "#FFFFFF",
    "surface": "#F1F3F2",
    "text": "#252D2B",
    "muted": "#68736E",
    "border": "#D9E0DB",
    "forest": "#245B45",
    "green": "#287A5A",
    "sage": "#B5C9B8",
    "terracotta": "#D17A48",
    "blue": "#526B91",
    "plum": "#8A6599",
    "ochre": "#D1A34A",
}

SERIES_COLORS = [
    COLORS["green"],
    COLORS["terracotta"],
    COLORS["blue"],
    COLORS["plum"],
    COLORS["ochre"],
    "#289C9A",
    "#B65C72",
    "#768B42",
]

DISEASE_COLORS = {
    "Measles": COLORS["terracotta"],
    "Mumps": COLORS["blue"],
    "Rubella": COLORS["plum"],
}

COVERAGE_SCALE = [
    [0.0, "#EFF5F0"],
    [0.5, "#8AB79C"],
    [1.0, "#245B45"],
]

INCIDENCE_SCALE = [
    [0.0, "#FFF4EA"],
    [0.5, "#E8A675"],
    [1.0, "#A34F2F"],
]

# Convert state names to postal abbreviations for the U.S. map (choropleth) visualization(s)
STATE_ABBREVIATIONS = dict(zip(
    [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California",
        "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
        "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
        "Massachusetts", "Michigan", "Minnesota", "Mississippi",
        "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina",
        "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
        "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming"
    ],
    [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
))

# Configure dashboard page
st.set_page_config(
    page_title="Vaccination & Disease Surveillance",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cleaned HepB state-level data
@st.cache_data
def load_hepb_data():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "hepB"
        / "cleaned"
        / "HepB_Harmonized_Data.csv"
    )

    return pd.read_csv(file_path)

# Load HepB fixed effects regression results
@st.cache_data
def load_hepb_regression_results():
    analysis_folder = (
        Path(__file__).resolve().parent
        / "data"
        / "hepB"
        / "analysis"
    )

    common_cohort = pd.read_csv(
        analysis_folder / "HepB_FixedEffects_Results.csv"
    )

    full_sample = pd.read_csv(
        analysis_folder / "HepB_FixedEffects_Lag0_FullSample.csv"
    )

    sensitivity = pd.read_csv(
        analysis_folder / "HepB_FixedEffects_Sensitivity.csv"
    )

    return common_cohort, full_sample, sensitivity

# Load historical HepB coverage + age specific incidence dataset(s)
@st.cache_data
def load_hepb_historical_data():
    data_folder = (
        Path(__file__).resolve().parent
        / "data"
        / "hepB"
        / "cleaned"
    )

    coverage = pd.read_csv(
        data_folder / "HepB_Historical_Coverage_1994_2014.csv"
    )

    incidence = pd.read_csv(
        data_folder / "HepB_AgeSpecific_Incidence_2003_2023.csv"
    )

    return coverage, incidence

# Load cleaned MMR state-level data
@st.cache_data
def load_mmr_data():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "cleaned"
        / "linked_state_year_no_offset.csv"
    )

    df = pd.read_csv(file_path)

# Keep primary MMR vaccination coverage observations
    mmr = df[
        (df["Vaccine"] == "MMR") &
        (df["Coverage_Source"] == "NIS") &
        (df["Age"] == "19-35 Months (survey)") &
        (df["Disease"].isin(["Measles", "Mumps", "Rubella"]))
    ].copy()

    return mmr

# Load MMR correlation analysis results
@st.cache_data
def load_mmr_correlation_results():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "analysis"
        / "correlations"
        / "correlation_summary.csv"
    )

    results = pd.read_csv(file_path)

    # Keep measles, mumps and rubella results
    mmr_results = results[
        (results["Vaccine"] == "MMR") &
        (results["Disease"].isin(["Measles", "Mumps", "Rubella"]))
    ].copy()

    return mmr_results

# Load MMR Poisson regression results
@st.cache_data
def load_mmr_poisson_results():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "analysis"
        / "correlations"
        / "correlation_summary.csv"
    )

    results = pd.read_csv(file_path)

    # Keep primary MMR regression results
    mmr_results = results[
        (results["Vaccine"] == "MMR") &
        (results["Disease"].isin(["Measles", "Mumps", "Rubella"]))
    ].copy()

    return mmr_results[
        [
            "Disease",
            "N",
            "RateRatio_per_10pts",
            "RR_CI_low",
            "RR_CI_high",
            "RR_p"
        ]
    ]

# Load MMR time lag correlation results
@st.cache_data
def load_mmr_lag_results():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "analysis"
        / "correlations"
        / "lag_correlations.csv"
    )

    results = pd.read_csv(file_path)

    # Keep measles, mumps and rubella results
    mmr_results = results[
        results["Disease"].isin(["Measles", "Mumps", "Rubella"])
    ].copy()

    return mmr_results

# Load MMR data-alignment sensitivity results
@st.cache_data
def load_mmr_offset_results():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "analysis"
        / "correlations"
        / "offset_comparison.csv"
    )

    results = pd.read_csv(file_path)

    # Keep MMR results for measles, mumps and rubella
    mmr_results = results[
        (results["Vaccine"] == "MMR") &
        (results["Disease"].isin(["Measles", "Mumps", "Rubella"]))
    ].copy()

    return mmr_results

# Load historical measles positive-control results
@st.cache_data
def load_mmr_historical_results():
    file_path = (
        Path(__file__).resolve().parent
        / "data"
        / "mmr"
        / "analysis"
        / "correlations"
        / "positive_control_measles.csv"
    )

    return pd.read_csv(file_path)

# Dashboard styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {COLORS["background"]};
        color: {COLORS["text"]};
    }}

    [data-testid="stSidebar"] {{
        background-color: {COLORS["surface"]};
        border-right: 1px solid {COLORS["border"]};
    }}

    .block-container {{
        max-width: 1150px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3 {{
        color: {COLORS["text"]};
        font-weight: 600;
        letter-spacing: -0.025em;
    }}

    h1 {{
        line-height: 1.2;
    }}

    p {{
        line-height: 1.7;
    }}

    div.stButton > button {{
        background-color: transparent;
        color: {COLORS["forest"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        font-weight: 500;
    }}

    div.stButton > button:hover {{
        color: {COLORS["forest"]};
        background-color: {COLORS["surface"]};
        border-color: {COLORS["forest"]};
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-color: {COLORS["border"]};
    }}

    .figure-caption {{
        font-size: 0.88rem;
        font-style: italic;
        color: {COLORS["muted"]};
        line-height: 1.6;
        margin-top: -0.4rem;
        margin-bottom: 1.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Display standardized academic figure captions
def figure_caption(number, description):
    st.markdown(
        f'<p class="figure-caption"><strong>Figure {number}.</strong> '
        f'{description}</p>',
        unsafe_allow_html=True
    )

# Define 5 pages of the dashboard
pages = {
    "Overview": "Overview",
    "1.  Measles, Mumps, and Rubella": "MMR Analysis",
    "2.  HepB · State-Level": "HepB State-Level",
    "3.  HepB · Historical": "HepB Historical",
    "4.  Methods and Limitations": "Methods and Limitations"
}

if "page" not in st.session_state:
    st.session_state.page = "Overview"

# Create sidebar for navigation
with st.sidebar:
    st.markdown("### Vaccination and Disease")
    st.caption("Computational Research Dashboard")
    st.divider()

    st.caption("CONTENTS:")

    selected_page = st.radio("Research navigation", options=list(pages.values()), format_func=lambda page: next(
            label for label, value in pages.items()
            if value == page
        ),
        key="page", label_visibility="collapsed")

    st.divider()
    st.caption("UMGC Fall 2026 / MS Biotechnology / Vaccination Group 3")

# Create navigation cards
def go_to_page(destination):
    st.session_state.page = destination

def research_card(number, title, description, destination, key, category):
    with st.container(border=True):
        st.caption(f"{number} / {category}")
        st.markdown(f"#### {title}")
        st.caption(description)

        st.button("Explore →", key=key, on_click=go_to_page, args=(destination,))

# Overview page functionality
if selected_page == "Overview":
    st.caption("AN INTERACTIVE COMPUTATIONAL PUBLIC HEALTH RESEARCH STUDY")

    st.title("Vaccination & the Return of 'Eliminated' Diseases")

    st.write(
        "How do changes in childhood vaccination coverage "
        "relate to the incidence of vaccine-preventable diseases?"
    )

    st.caption(
        "An exploratory ecological analysis of vaccination coverage "
        "and reported disease incidence across the United States, "
        "using interactive visualizations and state-level surveillance data."
    )

    st.divider()

    left_column, right_column = st.columns(2, gap="large")

    with left_column:
        research_card(
            "1",
            "Measles, Mumps, and Rubella",
            "Vaccination trends, disease incidence, and statistical associations.",
            "MMR Analysis",
            "mmr_card",
            "COVERAGE & INCIDENCE"
        )

        research_card(
            "3",
            "Hepatitis B: Historical",
            "Long term vaccination trends and age specific disease incidence.",
            "HepB Historical",
            "historical_card",
            "HISTORICAL CONTEXT"
        )

    with right_column:
        research_card(
            "2",
            "Hepatitis B: State-Level",
            "Geographic patterns, time lags, and fixed effects regression.",
            "HepB State-Level",
            "state_card",
            "STATE-LEVEL ANALYSIS"
        )

        research_card(
            "4",
            "Methods and Limitations",
            "Data sources, harmonization, validation, and study limitations.",
            "Methods and Limitations",
            "methods_card",
            "METHODOLOGY"
        )

    # Historical and public health context
    st.divider()

    with st.expander("Background and Public Health Context", expanded=False):

        st.markdown("#### MMR Vaccination and Measles Elimination")

        st.write(
            "Vaccination has substantially reduced the burden of measles, "
            "mumps, and rubella in the United States. The first measles "
            "vaccine was licensed in 1963, followed by the combined "
            "measles, mumps, and rubella (MMR) vaccine in 1971. A routine "
            "second dose was recommended in 1989 to improve protection "
            "against measles. In 2000, measles was declared effectively eliminated "
            "from the United States, meaning continuous endemic transmission "
            "had been interrupted for at least 12 months. Elimination does "
            "not mean imported cases or subsequent outbreaks cannot occur."
        )

        st.markdown("#### Hepatitis B Vaccination and Acute Infection")

        st.write(
            "Hepatitis B virus (HBV) can cause acute infection or persistent, "
            "chronic infection. The risk of developing chronic infection "
            "is particularly high when HBV is contracted during infancy or "
            "early childhood. In 1991, the United States adopted a "
            "universal infant hepatitis B vaccination strategy to prevent "
            "infection and its long term complications. Acute hepatitis B "
            "surveillance measures reported new acute infections rather "
            "than the total burden of chronic hepatitis B."
        )

        st.caption(
            "In this study, childhood HepB vaccination coverage is "
            "compared with reported acute hepatitis B incidence across "
            "all ages. These measures represent different populations, "
            "which is an important limitation when interpreting results."
        )

        st.markdown("#### Vaccination Recommendations and Requirements")

        st.write(
            "Vaccination recommendations and school-entry requirements "
            "serve similar but distinct purposes. National recommendations "
            "inform clinical vaccination practices, while state laws "
            "establish immunization mandates for school attendance. "
            "Requirements and exemption policies vary by state and may "
            "change over time, providing important insight into geographic "
            "differences in vaccination coverage."
        )

        st.caption(
            "This dashboard examines state-level vaccination coverage "
            "and disease incidence, but does not directly evaluate "
            "vaccination mandates, exemption policies, or their effects."
        )

        st.markdown("**Background References**")

        st.markdown(
            "- [CDC: History of Measles]"
            "(https://www.cdc.gov/measles/about/history-of-measles.html)\n"
            "- [CDC: Hepatitis B Overview]"
            "(https://www.cdc.gov/hepatitis-b/about/index.html)\n"
            "- [CDC: Hepatitis B Vaccination Recommendations]"
            "(https://www.cdc.gov/mmwr/volumes/67/rr/rr6701a1.htm)\n"
            "- [CDC: State Vaccination Requirements]"
            "(https://www.cdc.gov/vaccines/php/requirements-laws/"
            "state-vaccination-requirements.html)"
        )

    st.info(
        "These findings represent ecological, population-level associations "
        "and should not be interpreted as evidence of causal relationships."
    )

# MMR analysis page
elif selected_page == "MMR Analysis":
    st.caption("1 / MEASLES, MUMPS, AND RUBELLA")
    st.title("Measles, Mumps, and Rubella")

    st.write(
        "Investigate childhood MMR vaccination coverage "
        "and reported disease incidence across U.S. states."
    )

    st.divider()
    st.subheader("Coverage and Incidence Trends")

    # Load validated MMR state-level data
    mmr_data = load_mmr_data()

    # Initialize chart selections before rendering their widgets
    if "mmr_coverage_states" not in st.session_state:
        st.session_state.mmr_coverage_states = []

    if "mmr_incidence_states" not in st.session_state:
        st.session_state.mmr_incidence_states = []

    if "mmr_map_selection_version" not in st.session_state:
        st.session_state.mmr_map_selection_version = 0

    # Interactive geographic comparison
    st.markdown("#### Geographic Distribution")

    st.write(
        "Explore how childhood MMR vaccination coverage and "
        "reported disease incidence varies across the United States. "
        "Choose a metric and year to update the map."
    )

    map_metric = st.selectbox(
        "Map metric",
        options=[
            "MMR vaccination coverage",
            "Measles incidence",
            "Mumps incidence",
            "Rubella incidence"
        ],
        key="mmr_map_metric"
    )

    map_year = st.select_slider(
        "Map year",
        options=sorted(mmr_data["Year"].dropna().unique()),
        value=int(mmr_data["Year"].max()),
        key="mmr_map_year"
    )

    if map_metric == "MMR vaccination coverage":
        map_data = (
            mmr_data[mmr_data["Year"] == map_year]
            .groupby("State", as_index=False)["Coverage"]
            .mean()
        )

        map_value = "Coverage"
        map_label = "MMR vaccination coverage (%)"
        map_range = [0, 100]

    else:
        map_disease = map_metric.split(" ")[0]

        map_data = (
            mmr_data[
                (mmr_data["Year"] == map_year) &
                (mmr_data["Disease"] == map_disease)
            ]
            .groupby("State", as_index=False)["Rate_per_100k"]
            .mean()
        )

        map_value = "Rate_per_100k"
        map_label = "Reported incidence (per 100,000)"
        map_range = None

    # Match state names to Plotly map locations
    map_data["State_Code"] = map_data["State"].map(
        STATE_ABBREVIATIONS
    )

    map_data = map_data.dropna(
        subset=["State_Code", map_value]
    )

    if not map_data.empty:
        map_fig = px.choropleth(
            map_data,
            locations="State_Code",
            locationmode="USA-states",
            color=map_value,
            scope="usa",
            custom_data=["State"],
            color_continuous_scale=(
                COVERAGE_SCALE
                if map_metric == "MMR vaccination coverage"
                else INCIDENCE_SCALE
            ),
            range_color=map_range,
            labels={map_value: map_label},
            title=f"{map_metric}, {map_year}"
        )

        map_fig.update_traces(
            marker_line_color="white",
            marker_line_width=0.7,
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>" + map_label + ": %{z:.2f}"
                "<extra></extra>"
            )
        )

        map_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=0, r=0, t=60, b=0),
            height=500,
            coloraxis_colorbar=dict(
                title=dict(text=map_label)
            )
        )

        map_event = st.plotly_chart(
            map_fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode=("points", "box", "lasso"),
            key=f"mmr_map_selection_{st.session_state.mmr_map_selection_version}"
        )

        st.caption(
            f"Displaying {len(map_data)} states with available "
            f"observations for {map_year}. States without available "
            "data are not assigned a color value."
        )

        figure_caption(
            1,
            "Geographic distribution of childhood MMR vaccination "
            "coverage or reported measles, mumps, and rubella incidence "
            "across U.S. states in a selected year. Coverage is "
            "expressed by percentage, and incidence is expressed as "
            "reported cases, per 100,000 population. States without "
            "available data are not assigned a value. "
        )

        selected_map_points = map_event.selection.points

        map_selected_states = sorted({
            point["customdata"][0]
            for point in selected_map_points
            if point.get("customdata")
        })

        if map_selected_states:
            st.caption(
                "Selected on map: " + ", ".join(map_selected_states)
            )
        else:
            st.caption(
                "Select states on the map to compare their trends below."
            )

        apply_column, reset_column = st.columns(2)

        with apply_column:
            if st.button(
                "Apply map selection to both charts below",
                disabled=not map_selected_states,
                use_container_width=True
            ):
                st.session_state.mmr_coverage_states = map_selected_states
                st.session_state.mmr_incidence_states = map_selected_states
                st.rerun()

        with reset_column:
            if st.button(
                "Reset map selection(s)",
                use_container_width=True
            ):
                st.session_state.mmr_coverage_states = []
                st.session_state.mmr_incidence_states = []
                st.session_state.mmr_map_selection_version += 1
                st.rerun()

    else:
        st.info(
            "No state-level observations are available for "
            "the selected metric and year."
        )

    st.divider()

    # Select states for visualization
    available_states = sorted(mmr_data["State"].unique())

    selected_coverage_states = st.multiselect(
        "Select state(s) for coverage",
        options=available_states,
        key="mmr_coverage_states"
    ) 
        
    # Filter coverage observations by state
    if selected_coverage_states:
        coverage_data = mmr_data[
            mmr_data["State"].isin(selected_coverage_states)
        ].copy()
    else:
        coverage_data = mmr_data.copy()

    # Calculate annual average vaccination coverage
    coverage_trends = (
        coverage_data
        .groupby(["State", "Year"], as_index=False)["Coverage"]
        .mean()
    )

    if selected_coverage_states:
        coverage_fig = px.line(
            coverage_trends.sort_values("Year"),
            x="Year",
            y="Coverage",
            color="State",
            markers=True,
            labels={
                "Year": "Survey Year",
                "Coverage": "MMR Vaccination Coverage (%)",
                "State": "State"
            },
            title="MMR Vaccination Coverage Over Time",
            color_discrete_sequence=SERIES_COLORS
        )
    else:
        national_trend = (
            coverage_trends
            .groupby("Year", as_index=False)["Coverage"]
                .mean()
        )

        coverage_fig = px.line(
            national_trend,
            x="Year",
            y="Coverage",
            markers=True,
            labels={
                "Year": "Survey Year",
                "Coverage": "Average State MMR Coverage (%)"
            },
            title="Average State MMR Vaccination Coverage, 1995–2023"
        )

        coverage_fig.update_traces(
            name="State average",
            line=dict(color=COLORS["green"], width=3),
            marker=dict(size=6)
        )

    coverage_fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b>"
            "<br>Survey year: %{x:.0f}"
            "<br>MMR coverage: %{y:.1f}%"
            "<extra></extra>"
        )
    )

    coverage_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(dtick=2),
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(coverage_fig, use_container_width=True)

    figure_caption(
        2,
        "MMR vaccination coverage among children aged 19–35 months, "
        "1995–2023. The default view represents the unweighted mean "
        "of state-level coverage estimates; selecting states displays "
        "their individual trends. Source: CDC National Immunization "
        "Survey (NIS-Child)."
    )

# Plot measles, mumps and rubella incidence over time
    st.divider()
    st.markdown("#### Disease Incidence Over Time")

    disease_column, state_column = st.columns(2)

    with disease_column:
        selected_mmr_disease = st.selectbox(
            "Select disease",
            options=["Measles", "Mumps", "Rubella"],
            key="mmr_disease"
        )

        selected_incidence_states = st.multiselect(
            "Select state(s) for incidence",
            options=available_states,
            key="mmr_incidence_states"
        )

    incidence_data = mmr_data[
        mmr_data["Disease"] == selected_mmr_disease
    ].copy()

    if selected_incidence_states:
        incidence_data = incidence_data[
            incidence_data["State"].isin(selected_incidence_states)
        ]

        incidence_trends = (
            incidence_data
            .sort_values("Year")
            [["State", "Year", "Rate_per_100k"]]
        )

        incidence_fig = px.line(
            incidence_trends,
            x="Year",
            y="Rate_per_100k",
            color="State",
            markers=True,
            labels={
                "Year": "Surveillance Year",
                "Rate_per_100k": "Incidence (per 100,000)",
                "State": "State"
            },
            title=f"{selected_mmr_disease} Incidence Over Time",
            color_discrete_sequence=SERIES_COLORS
        )

    else:
        incidence_trends = (
            incidence_data
            .groupby("Year", as_index=False)["Rate_per_100k"]
            .mean()
        )

        incidence_fig = px.line(
            incidence_trends,
            x="Year",
            y="Rate_per_100k",
            markers=True,
            labels={
                "Year": "Surveillance Year",
                "Rate_per_100k": "Average State Incidence (per 100,000)"
            },
            title=f"Average State {selected_mmr_disease} Incidence, 1995–2023"
        )

        incidence_fig.update_traces(
            name="State average",
            line=dict(color=COLORS["terracotta"], width=3),
            marker=dict(size=6)
        )

    incidence_fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b>"
            "<br>Surveillance year: %{x:.0f}"
            "<br>Incidence: %{y:.2f} per 100,000"
            "<extra></extra>"
        )
    )

    incidence_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(dtick=2)
    )

    st.plotly_chart(incidence_fig, use_container_width=True)

    figure_caption(
        3,
        "Reported measles, mumps, or rubella incidence across U.S. states, "
        "1995–2023. Incidence is expressed as reported cases, per 100,000 "
        "population. The default view shows the unweighted mean across "
        "states with observations available; selected states are displayed "
        "individually. Source: state-level disease surveillance data."
    )

    # Display MMR correlation analysis
    st.divider()
    st.subheader("Statistical Analysis")

    st.write(
        "Compare pooled Spearman correlations with correlations "
        "calculated after removing state-specific means from "
        "vaccination coverage and disease incidence."
    )

    mmr_correlations = load_mmr_correlation_results()

    # Prepare correlation estimates for comparison
    correlation_chart_data = mmr_correlations.melt(
        id_vars=["Disease"],
        value_vars=["Pooled_Spearman", "FE_Spearman"],
        var_name="Method",
        value_name="Correlation"
    )

    correlation_chart_data["Method"] = correlation_chart_data["Method"].replace({
        "Pooled_Spearman": "Pooled Spearman",
        "FE_Spearman": "State Mean Centered Spearman"
    })

    # Add confidence intervals for state mean centered estimates
    correlation_chart_data = correlation_chart_data.merge(
        mmr_correlations[
            ["Disease", "FE_Spearman", "FE_CI_low", "FE_CI_high"]
        ],
        on="Disease",
        how="left"
    )

    correlation_chart_data["CI_upper"] = 0.0
    correlation_chart_data["CI_lower"] = 0.0

    centered_rows = (
        correlation_chart_data["Method"] == "State Mean Centered Spearman"
    )

    correlation_chart_data.loc[centered_rows, "CI_upper"] = (
        correlation_chart_data.loc[centered_rows, "FE_CI_high"]
        - correlation_chart_data.loc[centered_rows, "Correlation"]
    )

    correlation_chart_data.loc[centered_rows, "CI_lower"] = (
        correlation_chart_data.loc[centered_rows, "Correlation"]
        - correlation_chart_data.loc[centered_rows, "FE_CI_low"]
    )

    correlation_fig = px.bar(
        correlation_chart_data,
        x="Disease",
        y="Correlation",
        color="Method",
        barmode="group",
        error_y="CI_upper",
        error_y_minus="CI_lower",
        color_discrete_map={
            "Pooled Spearman": COLORS["blue"],
            "State Mean Centered Spearman": COLORS["green"]
        },
        labels={
            "Disease": "Disease",
            "Correlation": "Spearman Correlation",
            "Method": "Analysis Method"
        },
        title="MMR Coverage vs. Disease Incidence"
    )

    correlation_fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b>"
            "<br>Method: %{fullData.name}"
            "<br>Spearman's ρ: %{y:.3f}"
            "<extra></extra>"
        )
    )

    correlation_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        yaxis=dict(zeroline=True, zerolinecolor="#6B7280")
    )

    st.plotly_chart(correlation_fig, use_container_width=True)

    figure_caption(
        4,
        "Associations between childhood MMR vaccination coverage and "
        "reported disease incidence, measured using pooled and "
        "state mean centered Spearman correlations. Error bars represent "
        "reported 95% confidence intervals for the centered estimates only. "
        "State mean centered correlations are not fixed effects "
        "regression coefficients."
    )

    # Display MMR correlation results table
    st.markdown("#### Correlation Results")

    correlation_table = mmr_correlations[
        [
            "Disease",
            "N",
            "Pooled_Spearman",
            "FE_Spearman",
            "FE_CI_low",
            "FE_CI_high"
        ]
    ].copy()

    correlation_table = correlation_table.rename(columns={
        "N": "State-year observations",
        "Pooled_Spearman": "Pooled Spearman's ρ",
        "FE_Spearman": "State mean centered Spearman's ρ",
        "FE_CI_low": "95% CI lower",
        "FE_CI_high": "95% CI upper"
    })

    st.dataframe(
        correlation_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "State-year observations": st.column_config.NumberColumn(
                "State-year observations", format="%d"
            ),
            "Pooled Spearman's ρ": st.column_config.NumberColumn(
                "Pooled Spearman's ρ", format="%.3f"
            ),
            "State mean centered Spearman's ρ": st.column_config.NumberColumn(
                "State mean centered Spearman's ρ", format="%.3f"
            ),
            "95% CI lower": st.column_config.NumberColumn(
                "95% CI lower", format="%.3f"
            ),
            "95% CI upper": st.column_config.NumberColumn(
                "95% CI upper", format="%.3f"
            )
        }
    )

    # Interpret MMR correlation findings
    st.markdown("#### Findings and Interpretation")

    st.write(
        "Across measles, mumps and rubella, pooled Spearman "
        "correlations between MMR vaccination coverage and "
        "reported disease incidence were weak and negative, "
        "ranging from -0.031 to -0.026."
    )

    st.write(
        "After removing state-specific averages, correlations "
        "stayed small. Measles (rho = -0.062) and rubella "
        "(rho = -0.058) had reported 95% confidence intervals "
        "that excluded zero, while the interval for mumps "
        "(rho = -0.011) included zero."
    )

    st.caption(
        "Although some confidence intervals excluded zero, the "
        "estimated correlations were small in magnitude. Outbreaks, "
        "population immunity, and reporting differences may contribute "
        "to variation in disease incidence reporting."
    )

    # Display MMR Poisson regression results
    st.divider()
    st.subheader("Poisson Regression Analysis")

    st.write(
        "Poisson regression models estimate the association between "
        "MMR vaccination coverage and reported disease incidence, "
        "accounting for state-specific differences and population size. "
        "Results are expressed as rate ratios for a 10% point "
        "increase in vaccination coverage."
    )

    poisson_results = load_mmr_poisson_results()

    # Plot rate ratios with 95% confidence intervals
    poisson_fig = px.scatter(
        poisson_results,
        x="RateRatio_per_10pts",
        y="Disease",
        error_x=(
            poisson_results["RR_CI_high"]
            - poisson_results["RateRatio_per_10pts"]
        ),
        error_x_minus=(
            poisson_results["RateRatio_per_10pts"]
            - poisson_results["RR_CI_low"]
        ),
        labels={
            "RateRatio_per_10pts": "Incidence Rate Ratio",
            "Disease": "Disease"
        },
        title="MMR Coverage and Disease Incidence: Poisson Regression"
    )

    poisson_fig.update_traces(
        marker=dict(color=COLORS["blue"], size=10),
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Incidence rate ratio: %{x:.3f}"
            "<extra></extra>"
        )
    )

    poisson_fig.add_vline(
        x=1,
        line_dash="dash",
        line_color="#6B7280"
    )

    poisson_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(type="log"),
        height=350
    )

    st.plotly_chart(poisson_fig, use_container_width=True)

    figure_caption(
        5,
        "Estimated incidence rate ratios associated with a "
        "10% point increase in MMR vaccination coverage. "
        "Horizontal bars represent reported 95% confidence intervals; "
        "the dashed reference line indicates a rate ratio of 1.0. "
        "Poisson models include state fixed effects, a population offset, "
        "and standard errors clustered by state."
    )

    # Display Poisson regression results table
    st.markdown("#### Regression Results")

    poisson_table = poisson_results.rename(columns={
        "N": "State-year observations",
        "RateRatio_per_10pts": "Incidence rate ratio",
        "RR_CI_low": "95% CI lower",
        "RR_CI_high": "95% CI upper",
        "RR_p": "p-value"
    })

    st.dataframe(
        poisson_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "State-year observations": st.column_config.NumberColumn(
                "State-year observations", format="%d"
            ),
            "Incidence rate ratio": st.column_config.NumberColumn(
                "Incidence rate ratio", format="%.3f"
            ),
            "95% CI lower": st.column_config.NumberColumn(
                "95% CI lower", format="%.3f"
            ),
            "95% CI upper": st.column_config.NumberColumn(
                "95% CI upper", format="%.3f"
            ),
            "p-value": st.column_config.NumberColumn(
                "p-value", format="%.3f"
            )
        }
    )

    # Interpret MMR Poisson regression findings
    st.markdown("#### Regression Findings and Interpretation")

    st.write(
        "The estimated incidence rate ratios were below 1.0 for "
        "all three diseases: measles (0.653), mumps (0.718) and "
        "rubella (0.401), respectively. This indicates that higher MMR coverage "
        "was associated with lower reported incidence in the "
        "fitted models, though the estimates were imprecise."
    )

    st.write(
        "All three 95% confidence intervals crossed 1.0, and "
        "none of the associations was statistically significant "
        "at the 0.05 level. The results therefore do not provide "
        "sufficient evidence of a consistent association after "
        "accounting for state-specific differences."
    )

    # Display MMR time lag analysis
    st.divider()
    with st.expander("Time Lag Analysis", expanded=False):

        st.write(
            "Explore whether MMR vaccination coverage is associated "
            "with reported disease incidence in following years. "
            "State mean centered Spearman correlations are compared "
            "across time lags of 0–3 years."
        )

        mmr_lag_results = load_mmr_lag_results()

        # Select coverage preceding disease incidence
        coverage_lags = mmr_lag_results[
            (mmr_lag_results["Vaccine"] == "MMR") &
            (mmr_lag_results["Direction"] == "coverage -> later disease")
        ].copy()

        # Plot correlations and confidence intervals
        lag_fig = px.line(
            coverage_lags.sort_values("Lag_years"),
            x="Lag_years",
            y="Spearman",
            color="Disease",
            markers=True,
            error_y=coverage_lags.sort_values("Lag_years")["CI_high"]
                    - coverage_lags.sort_values("Lag_years")["Spearman"],
            error_y_minus=coverage_lags.sort_values("Lag_years")["Spearman"]
                    - coverage_lags.sort_values("Lag_years")["CI_low"],
            color_discrete_map=DISEASE_COLORS,
            labels={
                "Lag_years": "Time Lag (Years)",
                "Spearman": "State Mean Centered Spearman Correlation",
                "Disease": "Disease"
            },
            title="MMR Coverage vs. Subsequent Disease Incidence"
        )

        lag_fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b>"
                "<br>Time lag: %{x:.0f} years"
                "<br>Spearman's ρ: %{y:.3f}"
                "<extra></extra>"
            )
        )

        lag_fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#6B7280"
        )

        lag_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(dtick=1)
        )

        st.plotly_chart(lag_fig, use_container_width=True)

        figure_caption(
            6,
            "State mean centered Spearman correlations between MMR "
            "vaccination coverage and disease incidence in the same year "
            "(lag0) or subsequent years (lags1–3). Error bars represent "
            "reported 95% confidence intervals."
        )

        # Compare disease incidence preceding vaccination coverage
        st.markdown("#### Reverse-Direction Analysis")

        st.write(
            "As a comparison, examine whether reported disease incidence "
            "is associated with MMR vaccination coverage in following years. "
            "This analysis uses time lags of 1–3 years."
        )

        reverse_lags = mmr_lag_results[
            (mmr_lag_results["Vaccine"] == "MMR") &
            (mmr_lag_results["Direction"] == "disease -> later coverage")
        ].copy()

        reverse_lags = reverse_lags.sort_values(
            ["Disease", "Lag_years"]
        )

        # Calculate confidence interval distances
        reverse_lags["CI_upper"] = (
            reverse_lags["CI_high"] - reverse_lags["Spearman"]
        )

        reverse_lags["CI_lower"] = (
            reverse_lags["Spearman"] - reverse_lags["CI_low"]
        )

        reverse_fig = px.line(
            reverse_lags,
            x="Lag_years",
            y="Spearman",
            color="Disease",
            markers=True,
            error_y="CI_upper",
            error_y_minus="CI_lower",
            color_discrete_map=DISEASE_COLORS,
            labels={
                "Lag_years": "Time Lag (Years)",
                "Spearman": "State Mean Centered Spearman Correlation",
                "Disease": "Disease"
            },
            title="Disease Incidence vs. Subsequent MMR Coverage"
        )

        reverse_fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b>"
                "<br>Time lag: %{x:.0f} years"
                "<br>Spearman's ρ: %{y:.3f}"
                "<extra></extra>"
            )
        )

        reverse_fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#6B7280"
        )

        reverse_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(dtick=1)
        )

        st.plotly_chart(reverse_fig, use_container_width=True)

        figure_caption(
            7,
            "State mean centered Spearman correlations between reported "
            "disease incidence and MMR vaccination coverage in subsequent "
            "years (lags 1–3). Error bars represent reported 95% "
            "confidence intervals."
        )

        # Interpret MMR time lag findings
        st.markdown("#### Time Lag Findings and Interpretation")

        st.write(
            "Associations between MMR vaccination coverage and subsequent "
            "disease incidence were generally weak across the 0–3-year "
            "time lags. Measles showed small negative correlations at "
            "lags 0, 1, and 2, while mumps and rubella showed no consistent "
            "pattern across the examined lags."
        )

        st.write(
            "The reverse-direction analysis, comparing disease incidence "
            "with vaccination coverage in subsequent years, also produced "
            "correlations close to zero. Together, these findings do not "
            "identify a clear or consistent time lag pattern across "
            "the three diseases."
        )

        st.caption(
            "Time lag estimates are exploratory. Sample sizes vary "
            "across lags, and outbreak variability may influence "
            "the observed associations."
        )

# Display MMR data-alignment sensitivity analysis
    st.divider()
    with st.expander(
        "Data-Alignment Sensitivity Analysis",
        expanded=False
    ):

        st.write(
            "Compare Poisson regression results using two approaches "
            "to aligning childhood MMR vaccination coverage with "
            "reported disease incidence. Both approaches use the "
            "2013–2022 comparison window."
        )

        mmr_offset_results = load_mmr_offset_results()

        # Prepare rate ratios and confidence intervals
        offset_chart_data = mmr_offset_results.copy()

        offset_chart_data["CI_upper"] = (
            offset_chart_data["RR_CI_high"]
            - offset_chart_data["RateRatio_per_10pts"]
        )

        offset_chart_data["CI_lower"] = (
            offset_chart_data["RateRatio_per_10pts"]
            - offset_chart_data["RR_CI_low"]
        )

        # Plot rate ratios by data-alignment approach
        offset_fig = px.scatter(
            offset_chart_data,
            x="RateRatio_per_10pts",
            y="Disease",
            color="Version",
            error_x="CI_upper",
            error_x_minus="CI_lower",
            color_discrete_sequence=[
                COLORS["green"],
                COLORS["plum"]
            ],
            labels={
                "RateRatio_per_10pts": "Incidence Rate Ratio",
                "Disease": "Disease",
                "Version": "Alignment Approach"
            },
            title="MMR Sensitivity Analysis: No Offset vs. Two Year Offset"
        )

        offset_fig.update_traces(
            marker=dict(size=10),
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Approach: %{fullData.name}"
                "<br>Incidence rate ratio: %{x:.3f}"
                "<extra></extra>"
            )
        )

        offset_fig.add_vline(
            x=1,
            line_dash="dash",
            line_color="#6B7280"
        )

        offset_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(type="log"),
            height=400
        )

        st.plotly_chart(offset_fig, use_container_width=True)

        figure_caption(
            8,
            "Comparison of estimated incidence rate ratios under "
            "no offset and two year offset alignment approaches. "
            "Both analyses use ChildVaxView vaccination coverage at "
            "24 months and 500 state-year observations per disease "
            "during 2013–2022. Horizontal bars represent reported "
            "95% confidence intervals; the dashed line indicates "
            "a rate ratio of 1.0."
        )

        # Display data-alignment sensitivity results table
        st.markdown("#### Sensitivity Analysis Results")

        offset_table = mmr_offset_results[
            [
                "Disease",
                "Version",
                "N",
                "RateRatio_per_10pts",
                "RR_CI_low",
                "RR_CI_high",
                "RR_p"
            ]
        ].copy()

        offset_table = offset_table.rename(columns={
            "Version": "Alignment approach",
            "N": "State-year observations",
            "RateRatio_per_10pts": "Incidence rate ratio",
            "RR_CI_low": "95% CI lower",
            "RR_CI_high": "95% CI upper",
            "RR_p": "p-value"
        })

        st.dataframe(
            offset_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "State-year observations": st.column_config.NumberColumn(
                    "State-year observations", format="%d"
                ),
                "Incidence rate ratio": st.column_config.NumberColumn(
                    "Incidence rate ratio", format="%.3f"
                ),
                "95% CI lower": st.column_config.NumberColumn(
                    "95% CI lower", format="%.3f"
                ),
                "95% CI upper": st.column_config.NumberColumn(
                    "95% CI upper", format="%.3f"
                ),
                "p-value": st.column_config.NumberColumn(
                    "p-value", format="%.3f"
                )
            }
        )

        # Interpret data-alignment sensitivity findings
        st.markdown("#### Sensitivity Findings and Interpretation")

        st.write(
            "The estimated rate ratios differed between the no offset "
            "and two year offset approaches. However, all six reported "
            "95% confidence intervals included 1.0, and none of the "
            "associations achieved statistical significance at the "
            "0.05 level."
        )

        st.write(
            "The wide confidence intervals indicate considerable "
            "uncertainty, particularly for measles and rubella. "
            "Although the estimated associations changed with the "
            "alignment approach, neither method provided strong evidence "
            "of an association between MMR coverage and reported "
            "disease incidence."
        )

        st.caption(
            "This comparison uses ChildVaxView coverage at 24 months "
            "for both alignment approaches. Because the primary MMR "
            "analysis uses NIS survey coverage at 19–35 months, "
            "differences between these results and the primary analysis "
            "cannot be attributed solely to the alignment approach."
        )

    # Display historical measles positive-control analysis
    st.divider()
    with st.expander("Historical Measles Analysis", expanded=False):

        st.write(
            "As a historical comparison, examine reported measles "
            "incidence before and after the widespread introduction of the "
            "measles vaccine in 1963. The analysis uses historical "
            "Project Tycho surveillance data."
        )

        historical_measles = load_mmr_historical_results()

        # Label the comparison periods
        historical_measles["Period_Label"] = historical_measles["Period"].replace({
            "1950-1962": "Pre-Vaccine (1950–1962)",
            "1964-1969": "Post-Introduction (1964–1969)"
        })

        # Plot average annual reported measles cases
        historical_fig = px.bar(
            historical_measles,
            x="Period_Label",
            y="Mean_cases_per_year",
            text="Mean_cases_per_year",
            color="Period_Label",
            color_discrete_map={
                "Pre-Vaccine (1950–1962)": COLORS["terracotta"],
                "Post-Introduction (1964–1969)": COLORS["green"]
            },
            labels={
                "Period_Label": "Historical Period",
                "Mean_cases_per_year": "Average Annual Reported Cases"
            },
            title="Reported Measles Cases Before and After Vaccine Introduction"
        )

        historical_fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b>"
                "<br>Average annual cases: %{y:,.0f}"
                "<extra></extra>"
            )
        )

        historical_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=20, r=20, t=60, b=20),
            yaxis=dict(tickformat=",", rangemode="tozero"),
            showlegend=False,
            height=400
        )

        st.plotly_chart(historical_fig, use_container_width=True)

        figure_caption(
            9,
            "Average annual reported measles cases across the 50 U.S. "
            "states before vaccine introduction (1950–1962) and after "
            "introduction (1964–1969). The vaccine introduction year, "
            "1963, is excluded. Reporting completeness varied across "
            "states and years. Source: Project Tycho."
        )

        # Summarize historical measles findings
        st.markdown("#### Historical Findings and Interpretation")

        pre_vaccine = historical_measles.loc[
            historical_measles["Period"] == "1950-1962",
            "Mean_cases_per_year"
        ].iloc[0]

        post_vaccine = historical_measles.loc[
            historical_measles["Period"] == "1964-1969",
            "Mean_cases_per_year"
        ].iloc[0]

        percent_change = (post_vaccine - pre_vaccine) / pre_vaccine * 100

        st.metric(
            "Change in Average Annual Reported Measles Cases",
            f"{percent_change:.1f}%"
        )

        st.write(
            f"Average annual reported measles cases declined from "
            f"{pre_vaccine:,.0f} during 1950–1962 to "
            f"{post_vaccine:,.0f} during 1964–1969, "
            f"representing a {abs(percent_change):.1f}% decrease."
        )

        st.caption(
            "Historical reporting completeness varied by state and "
            "year. The comparison periods also differ in length, "
            "so annual averages are used rather than cumulative totals."
        )

# Hepatitis B state-level analysis page
elif selected_page == "HepB State-Level":
    st.caption("2 / HEPATITIS B")
    st.title("State-Level Associations")

    st.write(
        "Examine relationships between childhood hepatitis B "
        "vaccination coverage and reported acute hepatitis B "
        "incidence across U.S. states."
    )

    st.divider()
    st.subheader("State-Level Analysis")

# Load harmonized HepB data
    hepb_data = load_hepb_data()

# Filter observations by time lag and state
    lag_column, state_column = st.columns(2)

    with lag_column:
        selected_lag = st.selectbox(
            "Time lag (years)",
            options=sorted(hepb_data["lag"].dropna().unique()),
            index=0
        )

    with state_column:
        selected_states = st.multiselect(
            "Select state(s)",
            options=sorted(hepb_data["state"].dropna().unique()),
            default=[]
        )

    filtered_data = hepb_data[
        hepb_data["lag"] == selected_lag
    ].copy()

    if selected_states:
        filtered_data = filtered_data[
            filtered_data["state"].isin(selected_states)
        ]

# Plot vaccination coverage against acute HepB incidence
    fig = px.scatter(
        filtered_data,
        x="hepb_3dose_pct",
        y="acute_hepb_rate",
        custom_data=[
            "state",
            "coverage_birth_year",
            "incidence_year"
        ],
        labels={
            "hepb_3dose_pct": "HepB 3 Dose Coverage (%)",
            "acute_hepb_rate": "Acute HepB Incidence (per 100,000)"
        },
        title="Vaccination Coverage vs. Acute HepB Incidence"
    )

    fig.update_traces(
        marker=dict(
            color=COLORS["green"],
            size=8,
            opacity=0.65
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b>"
            "<br>Birth cohort: %{customdata[1]}"
            "<br>Surveillance year: %{customdata[2]}"
            "<br>HepB coverage: %{x:.1f}%"
            "<br>Acute HepB incidence: %{y:.2f} per 100,000"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    figure_caption(
        10,
        "Relationship between childhood three dose HepB vaccination "
        "coverage and reported acute hepatitis B incidence across "
        "U.S. states. Each point represents a state-level observation "
        "at the selected time lag. Incidence is expressed as cases, "
        "per 100,000 population."
    )

    st.caption(
        f"Displaying {len(filtered_data):,} observations "
        f"at lag{selected_lag}."
    )

# Plot acute HepB incidence over time
    st.subheader("Acute HepB Incidence Over Time")

    if selected_states:
        trend_data = filtered_data[
            ["state", "incidence_year", "acute_hepb_rate"]
        ].dropna().drop_duplicates()

        trend_fig = px.line(
            trend_data,
            x="incidence_year",
            y="acute_hepb_rate",
            color="state",
            markers=True,
            color_discrete_sequence=SERIES_COLORS,
            labels={
                "incidence_year": "Incidence Year",
                "acute_hepb_rate": "Acute HepB Incidence (per 100,000)",
                "state": "State"
            }
        )

        trend_fig.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b>"
                "<br>Surveillance year: %{x:.0f}"
                "<br>Acute HepB incidence: %{y:.2f} per 100,000"
                "<extra></extra>"
            )
        )

        trend_fig.update_layout(
            template="plotly_white",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(dtick=1)
        )

        st.plotly_chart(trend_fig, use_container_width=True)

        figure_caption(
            11,
            "Reported acute hepatitis B incidence over time for "
            "selected U.S. states. Rates are expressed as reported "
            "cases, per 100,000 population."
        )

    else:
        st.info(
            "Select one or more states above to display "
            "their acute HepB incidence trends."
        )

    
    with st.expander("View underlying data"):
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )

# Display fixed effects regression results
    st.divider()
    st.subheader("Statistical Analysis")

    st.write(
        "Two way, fixed effects regression models estimate "
        "associations between HepB vaccination coverage and "
        "acute HepB incidence, accounting for state and year "
        "effects. Standard errors are clustered by state."
    )

    common_cohort, full_sample, sensitivity = load_hepb_regression_results()

# Primary analysis: commoncohort lag comparison
    st.markdown("#### Primary Analysis: Time Lag Analysis")

    st.caption(
        "Birth cohorts 2011–2021. The common cohort window "
        "supports comparisons across lags 0, 1, and 2."
    )

    st.dataframe(
        common_cohort,
        use_container_width=True,
        hide_index=True,
        column_config={
            "lag": st.column_config.NumberColumn("Time lag (years)", format="%d"),
            "observations": st.column_config.NumberColumn(
                "State-year observations", format="%d"
            ),
            "coefficient": st.column_config.NumberColumn(
                "Estimated coefficient", format="%.4f"
            ),
            "p_value": st.column_config.NumberColumn("p-value", format="%.4f"),
            "ci_lower": st.column_config.NumberColumn("95% CI lower", format="%.4f"),
            "ci_upper": st.column_config.NumberColumn("95% CI upper", format="%.4f")
        }
    )

# Plot regression coefficients with confidence intervals
    coefficient_data = common_cohort.copy()
    coefficient_data["lag_label"] = coefficient_data["lag"].apply(
        lambda lag: f"Lag {int(lag)}"
    )

    coefficient_fig = px.scatter(
        coefficient_data,
        x="coefficient",
        y="lag_label",
        error_x=coefficient_data["ci_upper"] - coefficient_data["coefficient"],
        error_x_minus=coefficient_data["coefficient"] - coefficient_data["ci_lower"],
        labels={
            "coefficient": "Regression Coefficient",
            "lag_label": "Time Lag"
        },
        title="Fixed Effects Estimates by Time Lag"
    )

    coefficient_fig.update_traces(
        marker=dict(color=COLORS["blue"], size=10),
        hovertemplate=(
            "<b>%{y}</b>"
            "<br>Estimated coefficient: %{x:.4f}"
            "<extra></extra>"
        )
    )

    coefficient_fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="#6B7280"
    )

    coefficient_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        yaxis=dict(categoryorder="array", categoryarray=["Lag2", "Lag1", "Lag0"]),
        height=350
    )

    st.plotly_chart(coefficient_fig, use_container_width=True)

    figure_caption(
        12,
        "Estimated associations between childhood HepB vaccination "
        "coverage and acute hepatitis B incidence from two-way "
        "fixed effects regression models at lags of 0, 1, and 2 years. "
        "Horizontal bars represent 95% confidence intervals; the "
        "dashed reference line indicates a coefficient of zero. "
        "Models adjust for state and incidence year effects."
    )

    # Interpret primary fixed effects results
    st.markdown("#### Findings and Interpretation")

    st.write(
        "Across time lags of 0, 1, and 2 years, estimated associations "
        "between childhood HepB vaccination coverage and acute HepB "
        "incidence were small and not statistically significant. "
        "All three 95% confidence intervals included zero."
    )

    st.caption(
        "Childhood vaccination coverage and all age acute HepB "
        "incidence represent different populations, which limits "
        "the interpretation of these associations."
    )

# Supplementary analysis: full-sample lag0 regression
    with st.expander("Supplementary Analysis: Full Sample Lag0"):
        st.write(
            "This model uses all available lag0 observations, "
            "including the 2022 birth cohort."
        )

        st.dataframe(
            full_sample,
            use_container_width=True,
            hide_index=True
        )

# Sensitivity analysis: exclude West Virginia
    with st.expander("Sensitivity Analysis: Excluding West Virginia"):
        st.write(
            "Exploratory examination of acute hepatitis B surveillance "
            "data identified West Virginia as a potentially influential "
            "state, accounting for 8 of the 10 highest observed state-year "
            "incidence rates during the 2011–2018 period. To assess whether these "
            "unusually high rates influenced the regression estimates, "
            "the common cohort models were repeated after excluding "
            "West Virginia."
        )

        st.caption(
            "West Virginia remains included in the primary analysis. "
            "Its exclusion is used solely as a sensitivity check."
        )

        st.dataframe(
            sensitivity,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "All reported models use state and incidence year fixed "
        "effects with standard errors clustered by state. "
        "Results are from the predefined analysis samples and "
        "do not change live with the interactive chart filters."
    )

# Hepatitis B historical analysis page
elif selected_page == "HepB Historical":
    st.caption("3 / HEPATITIS B")
    st.title("Historical Trends")

    st.write(
        "Evaluate historical hepatitis B vaccination coverage "
        "and age specific acute hepatitis B incidence."
    )

    
    st.divider()
    st.subheader("Historical Analysis")

# Load historical HepB datasets
    historical_coverage, historical_incidence = load_hepb_historical_data()

# Plot national HepB vaccination coverage over time
    st.markdown("#### Childhood HepB Vaccination Coverage")

    st.write(
        "National three dose hepatitis B vaccination coverage "
        "among children, based on CDC NIS-Child estimates from "
        "1994-2014."
    )

    coverage_fig = px.line(
        historical_coverage.sort_values("survey_year"),
        x="survey_year",
        y="hepb_3dose_coverage",
        markers=True,
        labels={
            "survey_year": "Survey Year",
            "hepb_3dose_coverage": "HepB 3 Dose Coverage (%)"
        },
        title="National Childhood HepB Vaccination Coverage, 1994–2014"
    )

    coverage_fig.update_traces(
        line=dict(color=COLORS["green"], width=3),
        marker=dict(size=7),
        hovertemplate=(
            "Survey year: %{x:.0f}"
            "<br>Three dose HepB coverage: %{y:.1f}%"
            "<extra></extra>"
        )
    )

    coverage_fig.update_layout(
        template="plotly_white",
        title_x=0,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(dtick=2),
        yaxis=dict(range=[0, 100])
    )

    st.plotly_chart(coverage_fig, use_container_width=True)

    figure_caption(
        13,
        "National three dose hepatitis B vaccination coverage "
        "among children, 1994–2014. Values represent annual "
        "coverage estimates from the CDC National Immunization "
        "Survey (NIS-Child)."
    )


# Plot age specific acute HepB incidence over time
    st.divider()
    st.markdown("#### Acute HepB Incidence by Age Group")

    st.write(
        "Explore national acute hepatitis B incidence trends "
        "across age groups from 2003-2023, based on "
        "CDC hepatitis surveillance data."
    )

# Select age groups for comparison
    age_groups = sorted(historical_incidence["age_group"].dropna().unique())

    with st.expander("Customize age groups", expanded=False):
        selected_age_groups = st.multiselect(
            "Select age groups to display",
            options=age_groups,
            default=age_groups,
            key="historical_age_groups"
        )

    incidence_filtered = historical_incidence[
        historical_incidence["age_group"].isin(selected_age_groups)
    ].copy()

    if not incidence_filtered.empty:
        incidence_fig = px.line(
            incidence_filtered.sort_values("year"),
            x="year",
            y="acute_hepb_rate",
            color="age_group",
            markers=True,
            color_discrete_sequence=SERIES_COLORS,
            labels={
                "year": "Surveillance Year",
                "acute_hepb_rate": "Acute HepB Incidence (per 100,000)",
                "age_group": "Age Group"
            },
            title="Age Specific Acute HepB Incidence, 2003–2023"
        )

        incidence_fig.update_traces(
            hovertemplate=(
                "<b>Age group: %{fullData.name}</b>"
                "<br>Surveillance year: %{x:.0f}"
                "<br>Acute HepB incidence: %{y:.2f} per 100,000"
                "<extra></extra>"
            )
        )

        incidence_fig.update_layout(
            template="plotly_white",
            title_x=0,
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(dtick=2),
            legend_title_text="Age Group"
        )

        st.plotly_chart(incidence_fig, use_container_width=True)

        figure_caption(
            14,
            "Age specific trends in reported acute hepatitis B "
            "incidence in the United States, 2003–2023. Incidence "
            "rates are expressed as cases, per 100,000 population "
            "for each age group. Source: CDC Hepatitis Surveillance."
        )

    else:
        st.info("Select at least one age group to display incidence trends.")

# Summarize historical HepB findings
    st.divider()
    st.markdown("#### Historical Findings and Interpretation")

    st.write(
        "National childhood HepB three dose vaccination coverage "
        "increased substantially during the 1990s, rising from "
        "37% in 1994 to approximately 90% by 2000. Coverage "
        "subsequently remained relatively high through 2014."
    )

    st.write(
        "Over the 2003–2023 surveillance period, reported acute "
        "HepB incidence declined across multiple adult age groups. "
        "Among adults aged 20–29 years, incidence decreased from "
        "4.3 to 0.5 cases, per 100,000 population. Among those "
        "aged 30–39 years, incidence decreased from 5.1 to 0.7 "
        "cases, per 100,000 population."
    )

    st.caption(
        "The coverage and incidence datasets represent different "
        "populations and observation periods. These trends should "
        "therefore be considered separately rather than interpreted "
        "as a direct coverage/incidence comparison."
    )

# Methods and limitations page
elif selected_page == "Methods and Limitations":
    st.caption("4 / RESEARCH FRAMEWORK")
    st.title("Methods and Limitations")

    st.write(
        "This study examines relationships between childhood "
        "vaccination coverage and reported vaccine-preventable "
        "disease incidence using publicly available surveillance "
        "data. Analyses are observational and conducted primarily "
        "at the U.S. state level."
    )

    st.divider()

    # Describe data sources and alignment
    with st.expander("Data Sources and Harmonization", expanded=False):
        st.markdown("#### MMR Data")

        st.write(
            "The primary MMR analysis combines CDC National "
            "Immunization Survey (NIS-Child) coverage estimates "
            "for children aged 19–35 months with state-level "
            "measles, mumps and rubella surveillance data "
            "from 1995–2023."
        )

        st.write(
            "Coverage and incidence are linked by state and year. "
            "An additional sensitivity analysis uses ChildVaxView "
            "coverage estimates at 24 months to compare no offset "
            "and two year offset alignment approaches during "
            "2013–2022."
        )

        st.markdown("#### Hepatitis B Data")

        st.write(
            "The HepB analysis uses three dose childhood vaccination "
            "coverage estimates for birth cohorts 2011–2022 and "
            "reported state-level acute hepatitis B incidence. "
            "Coverage is aligned with incidence using time lags "
            "of 0, 1, and 2 years."
        )

        st.write(
            "A common birth-cohort window of 2011–2021 supports "
            "comparisons across the three lag specifications. "
            "Separate historical datasets describe national "
            "childhood vaccination coverage and age specific "
            "acute hepatitis B incidence."
        )

        st.caption(
            "The MMR and HepB analyses use different coverage "
            "definitions and alignment approaches. Their numerical "
            "estimates should not be treated as directly comparable."
        )

    # Explain statistical analyses
    with st.expander("Statistical Methods"):
        st.markdown("#### Correlation Analysis")

        st.write(
            "MMR associations are evaluated using pooled Spearman "
            "rank correlations and correlations calculated after "
            "subtracting state-specific means from coverage and "
            "incidence. The centered correlations describe "
            "variations within states but are not fixed effects "
            "regression coefficients."
        )

        st.markdown("#### Regression Analysis")

        st.write(
            "MMR Poisson regression models estimate incidence rate "
            "ratios for a 10% point increase in vaccination "
            "coverage. Models include state fixed effects, a "
            "population offset, and standard errors clustered "
            "by state."
        )

        st.write(
            "HepB analyses use two way, fixed effects regression "
            "models with state and incidence year effects and "
            "standard errors clustered by state. Coefficients "
            "are examined across lags of 0, 1, and 2 years."
        )

        st.markdown("#### Statistical Uncertainty")

        st.write(
            "Reported estimates are accompanied by 95% confidence "
            "intervals, where available. Intervals crossing zero "
            "for correlations or regression coefficients, or "
            "crossing 1.0 for incidence rate ratios, indicate "
            "that the corresponding estimates are not statistically "
            "significant at the typical 0.05 level."
        )

    # Describe sensitivity and historical comparisons
    with st.expander("Validation and Sensitivity Analyses"):
        st.markdown("#### MMR Time Lag Comparisons")

        st.write(
            "State mean centered Spearman correlations compare "
            "vaccination coverage with disease incidence in the "
            "same year and up to three following years. "
            "Reverse-direction comparisons examine whether "
            "reported incidence is associated with vaccination "
            "coverage in later years."
        )

        st.markdown("#### MMR Alignment Sensitivity")

        st.write(
            "No offset and two year offset alignment approaches "
            "are compared using the same ChildVaxView coverage "
            "definition and 2013–2022 analysis window."
        )

        st.markdown("#### HepB Sensitivity Analyses")

        st.write(
            "A supplementary HepB regression uses the full "
            "available lag0 sample. Additional models exclude "
            "West Virginia to examine the sensitivity of "
            "estimates to that particular state's observations."
        )

        st.markdown("#### Historical Comparisons")

        st.write(
            "Historical measles surveillance data from Project "
            "Tycho are used to compare average annual reported "
            "cases before and after widespread vaccine introduction in 1963. "
            "Separate HepB historical figures describe childhood "
            "vaccination coverage and age specific acute incidence."
        )

    # Centralize interpretation limitations
    with st.expander("Limitations and Confounding"):
        st.markdown("#### Ecological Study Design")

        st.write(
            "State-level associations do not establish individual-level "
            "vaccine effectiveness or causal relationships. "
            "Associations observed across populations may differ "
            "from those observed among individuals."
        )

        st.markdown("#### Population Differences")

        st.write(
            "Vaccination coverage estimates describe specific "
            "childhood populations, while disease surveillance "
            "may include broader age groups. This distinction "
            "is particularly important for HepB, where childhood "
            "coverage is compared with all age acute incidence."
        )

        st.markdown("#### Surveillance and Reporting")

        st.write(
            "Reported incidence can be influenced by case detection, "
            "reporting completeness, surveillance practices, and "
            "outbreak variability. Historical reporting practices "
            "may differ from those used in more recent periods."
        )

        st.markdown("#### Confounding and Time Alignment")

        st.write(
            "Population immunity, demographic differences, "
            "vaccination history, public health interventions, "
            "and other unmeasured factors may affect observed "
            "associations. Time lag comparisons are exploratory "
            "and do not independently establish the direction "
            "of a causal relationship."
        )

        st.markdown("#### Statistical Precision")

        st.write(
            "Sparse disease counts, incomplete observations, "
            "and wide confidence intervals can limit statistical "
            "precision. A non-significant association should not "
            "be interpreted as evidence that vaccination "
            "has no protective effect."
        )

    # Project team and academic attribution
    st.divider()
    st.subheader("Project Team & Attribution")

    st.write(
        "**University of Maryland Global Campus**  \n"
        "MS Biotechnology Capstone - Fall 2026  \n"
        "Dr. Wolfgang Rumpf  \n"
        "Vaccination Group 3"
    )

    st.markdown("**Research Group:**")

    st.write(
        "Liane Rosario  \n"
        "Amir Sadeghi  \n"
        "Nadin Salih  \n"
        "Maliha Shah"
    )

# Dashboard footer
st.divider()

st.caption(
    "UMGC MS Biotechnology Capstone · Vaccination Group 3"
)
