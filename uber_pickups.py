import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Uber pickups in NYC", page_icon="🚕", layout="wide")

st.title("🚕 Uber pickups in NYC")
st.caption("A sample of Uber pickups in New York City, September 2014 "
           "(the first 10,000 records of the public Streamlit demo dataset).")

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

# ---- Sidebar controls -------------------------------------------------------
st.sidebar.header("Controls")
hour_to_filter = st.sidebar.slider('hour', 0, 23, 17)   # min: 0h, max: 23h, default: 17h
show_raw = st.sidebar.checkbox('Show raw data')
st.sidebar.caption("Move the slider to see where pickups happen at different times of day.")

# ---- Numbers ----------------------------------------------------------------
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
busiest_hour = int(hist_values.argmax())
selected_count = int(hist_values[hour_to_filter])
average_per_hour = hist_values.mean()

c1, c2, c3 = st.columns(3)
c1.metric("Pickups in this sample", f"{len(data):,}")
c2.metric("Busiest hour", f"{busiest_hour}:00", f"{int(hist_values[busiest_hour])} pickups", delta_color="off")
c3.metric(f"Pickups at {hour_to_filter}:00", selected_count,
          f"{selected_count - average_per_hour:+.0f} vs the average hour")

# ---- Charts -----------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader('Number of pickups by hour')
    chart_df = pd.DataFrame({"hour": range(24), "pickups": hist_values})
    chart_df["selected"] = chart_df["hour"] == hour_to_filter
    bars = (alt.Chart(chart_df)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("hour:O", title="Hour of day"),
                y=alt.Y("pickups:Q", title="Pickups"),
                color=alt.condition(alt.datum.selected,
                                    alt.value("#FF4B4B"), alt.value("#7FC8FF")),
                tooltip=[alt.Tooltip("hour:O", title="Hour"),
                         alt.Tooltip("pickups:Q", title="Pickups")])
            .properties(height=380))
    st.altair_chart(bars, width="stretch")
    st.caption("The selected hour is highlighted in red.")

with right:
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
    st.subheader('Map of all pickups at %s:00' % hour_to_filter)
    st.map(filtered_data, size=30, color="#FF4B4B")
    st.caption(f"{len(filtered_data)} pickups shown.")

# ---- Raw data ---------------------------------------------------------------
if show_raw:
    st.subheader('Raw data')
    st.write(data)
