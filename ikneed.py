import base64

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from kneed import DataGenerator, KneeLocator

st.set_page_config(
    page_title="ikneed",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded",
)


# Intro
"""
## ikneed
Interactively find the point of maximum curvature in your data with the 
[kneed](https://github.com/arvkevi/kneed) Python package. This app lets 
you explore the effects of parameter tuning on the identified knee point. All 
of the parameters from the `KneeLocator` class are interactive in the sidebar. 
The figure will update when you change the parameters.
"""


@st.cache()
def find_knee(x, y, S, curve, direction, online, interp_method, polynomial_degree):
    kl = KneeLocator(
        x=x,
        y=y,
        S=S,
        curve=curve,
        direction=direction,
        online=online,
        interp_method=interp_method,
        polynomial_degree=polynomial_degree,
    )
    return kl


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False, sep="\t")
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="kneed_parameters.tsv">Download as .tsv</a>'
    return href


def plot_figure(x, y, kl, all_knees):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color="cornflowerblue", width=6),
            name="input data",
        )
    )
    if all_knees:
        fig.add_trace(
            go.Scatter(
                x=sorted(list(kl.all_knees)),
                y=list(kl.all_knees_y),
                mode="markers",
                marker=dict(
                    color="orange",
                    size=12,
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
                marker_symbol="circle",
                name="potential knee",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[kl.knee],
            y=[kl.knee_y],
            mode="markers",
            marker=dict(
                color="orangered",
                size=16,
                line=dict(width=1, color="DarkSlateGrey"),
            ),
            marker_symbol="x",
            name="knee point",
        )
    )
    fig.update_layout(
        title="Knee/Elbow(s) in Your Data",
        title_x=0.5,
        xaxis_title="x",
        yaxis_title="y",
    )
    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=4,
            ticks="outside",
            tickfont=dict(
                family="Arial",
                size=18,
                color="rgb(82, 82, 82)",
            ),
        ),
        yaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor="rgb(204, 204, 204)",
            linewidth=4,
            ticks="outside",
            tickfont=dict(
                family="Arial",
                size=18,
                color="rgb(82, 82, 82)",
            ),
        ),
        showlegend=True,
        plot_bgcolor="white",
    )
    return fig


def main():
    """
    The main function
    """
    default_x, default_y = DataGenerator.concave_increasing()
    # default_x, default_y = DataGenerator.bumpy()

    x_str = st.sidebar.text_area(
        "x (comma or new-line separated numbers)",
        value=(",").join(map(str, default_x)),
    )
    y_str = st.sidebar.text_area(
        "y (comma or new-line separated numbers",
        value=(",").join(map(str, default_y)),
    )

    # KneeLocator parameters
    S = st.sidebar.number_input(
        "S (sensitivity)", min_value=0.0, max_value=None, value=1.0, step=1.0
    )
    curve = st.sidebar.radio(
        "curve",
        ["concave", "convex"],
    )
    direction = st.sidebar.radio("direction", ["increasing", "decreasing"])
    online = st.sidebar.checkbox("online")
    interp_method = st.sidebar.radio("interp_method", ["interp1d", "polynomial"])

    # parse x and y
    try:
        x = [float(_) for _ in x_str.split(",")]
    except ValueError:
        x = [float(_) for _ in x_str.strip().split("\n")]
    try:
        y = [float(_) for _ in y_str.split(",")]
    except ValueError:
        y = [float(_) for _ in y_str.strip().split("\n")]

    polynomial_degree = 7
    if interp_method == "polynomial":
        polynomial_degree = st.sidebar.number_input(
            "polynomial_degree", min_value=1, max_value=99, value=7
        )

    kl = find_knee(x, y, S, curve, direction, online, interp_method, polynomial_degree)
    if interp_method == "polynomial":
        y = kl.Ds_y

    df = pd.DataFrame.from_dict(
        {
            "knee": [kl.knee],
            "S": [S],
            "curve": [curve],
            "direction": [direction],
            "online": [online],
            "interp_method": [interp_method],
            "polynomial_degree": [polynomial_degree],
            "x": [x_str],
            "y": [y_str],
        },
    )

    all_knees = st.checkbox("Show all knees/elbows")

    # plot the figure
    st.write(plot_figure(x, y, kl, all_knees))

    """
    Knee point found using each of the parameter sets:  
    """

    # dataframe knee logger w/ parameters
    # export dataframe
    st.dataframe(data=df)

    st.markdown(get_table_download_link(df), unsafe_allow_html=True)

    """
    All the parameters of the KneeLocator class from kneed:
    ```python
    kl = KneeLocator(
        x=x,
        y=y,
        S=S,
        curve=curve,
        direction=direction,
        online=online,
        interp_method=interp_method,
        polynomial_degree=polynomial_degree,
    )
    ```
    """


if __name__ == "__main__":
    main()
