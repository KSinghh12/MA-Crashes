#Khushi Singh CS230
#This program creates various charts and visualizations for mass cars crashes in MA in 2017.


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px

# [DA1] Clean the data
def load_data():
    # Load the data and I put the low memory because I saw it in a tutorial saying that it
    #allows pandas to load the entire file at once
    df = pd.read_csv('2017_Crashes.csv', low_memory=False)
    # [DA1] Clean the data by converting
    df['CRASH_DATETIME'] = pd.to_datetime(df['CRASH_DATETIME'])  # Converts the date part to datetime


    # [DA4] Filter the data by one condition by removing the invalid dates using the notna()
    df = df[df['CRASH_DATETIME'].notna()]
    return df



# [PY1] A function with two or more parameters, one of which has a default value
#Chart type is group because i wanted a grouped chart that can compare 2 towns
def compareplots(town_data, chosen_towns, chart_type='group'):
    if len(chosen_towns) == 2:
        #Check that the user chose two towns
        #group the data show it will still show the number of each type of accident when you hover
        #over the columns in the chart.

        # [DA7] Grouping data by 'CITY_TOWN_NAME' and 'MANR_COLL_DESCR' and counting occurrences
        datagroup = town_data.groupby(['CITY_TOWN_NAME', 'MANR_COLL_DESCR']).size().reset_index(name='counts')

        # use plotly to create the chart with the collision description and the number of each type
        fig_chart = px.bar(datagroup, x='MANR_COLL_DESCR', y='counts', color='CITY_TOWN_NAME', barmode=chart_type,
                           labels={'MANR_COLL_DESCR': 'Collision Description', 'counts': 'Count of Collisions'})
        st.plotly_chart(fig_chart)
    else:
        st.write("Please select exactly two towns for comparison.")

# [VIZ1], [VIZ4] Detailed map visualization with hover text
#Map Plot creates a map with the accidents plotted based on the month and collision description
def map_plot(month_data, chosen_month):
    #use the scatter geo function to create a map scatter plot with the longitude and latitude across America
    #The colors are different for each type of collision type and it corresponds to the chosen month
    fig_map = px.scatter_geo(month_data, lat='LAT', lon='LON', color='MANR_COLL_DESCR',
                         scope='usa', title=f'Car Crashes in MA for Month {chosen_month}',
                         hover_name='CITY_TOWN_NAME')
    #used chat gpt to create state lines for the locations
    fig_map.update_geos(
        visible=False,  # Turns off the base layer (you can turn it on if you want to see the default map)
        showsubunits=True,  # Shows state lines
        subunitcolor="black",  # Color for state lines
        fitbounds="locations"  # Fits the bounds to the locations
    )
#[PY5] A dictionary where you write code to access its keys, values, or items
    #used chatgpt to zoom in on MA using the longitude and latitude so it would be MA instead of the whole US
    fig_map.update_layout(
        geo=dict(
            scope='usa',
            lataxis=dict(range=[41.5, 42.9]),  # Latitude range for Massachusetts
            lonaxis=dict(range=[-73.5, -69.8]),  # Longitude range for Massachusetts
            landcolor='rgb(243, 243, 243)',  # Background color of the land
            lakecolor='rgb(255, 255, 255)'  # Color of the lakes
        )
    )


    st.plotly_chart(fig_map)

# [PY2] A function that returns more than one value

#Allows user to user the slider to choose a month and two towns
# that they want to look at for the grouped chart

# [DA5] Filtering data by month and by list of towns
def choosedata(df, month, towns):
    month_data = df[df['CRASH_DATETIME'].dt.month == month]
    town_data = df[df['CITY_TOWN_NAME'].isin(towns)]
    return month_data, town_data

# [VIZ2] Histogram chart
#Creates a histogram of the collision types over the month across MA
def plot_distribution(month_data, chosen_month):
    fig_hist = px.histogram(month_data, x='MANR_COLL_DESCR', title=f'Distribution of Crashes by Collision Description in Month {chosen_month}', labels={'MANR_COLL_DESCR': 'Collision Description'})
    st.plotly_chart(fig_hist)

#Pie chart to plot the levels of injury severity in total for MA

def injurysev_plot(df, chosen_month, chosen_town = 'All'):
    #the default view for the pie chart is all of MA injuries
    if chosen_town != 'All':
        df = df[df['CITY_TOWN_NAME'] == chosen_town]
    # Filter the data frame for the chosen month from the users side
    filterdf = df[df['CRASH_DATETIME'].dt.month == chosen_month]

    # [DA7] Counting injury severities
    # Count those injuries based on the filtered month
    injury_counts = filterdf['MAX_INJR_SVRTY_CL'].value_counts()
    # creates a subplot as a square 10x10
    fig, ax = plt.subplots(figsize=(10, 10))
    # creates injury counts as the index and the autopct sets up the formatting for the %s so its 1 decimal place
    ax.pie(injury_counts, labels=injury_counts.index, autopct='%1.1f%%', startangle=140)
    # sets the title of the pie chart so it shows for each month and the town specifics
    ax.set_title(f'Injury Severity Distribution in Month {chosen_month} - {chosen_town}')
    # makes the chart visible to the user on the streamlit app

    st.pyplot(fig)


def main():
    # [ST4] Page design features
    st.title('Welcome to the Mass Car Crashes in MA (2017) Data Explorer Homepage!')
    st.write('Learn more about the distributions of car accidents in Massachusetts through immersive visualizations.')

    df = load_data()

    # [ST1] Sidebar multi-select widget
    towns = df['CITY_TOWN_NAME'].unique()
    chosen_towns = st.sidebar.multiselect('Select two towns for comparison:', towns)
    # [ST2] Sidebar slider widget
    chosen_month = st.sidebar.slider('Select a month:', 1, 12, value=1)
    # [ST2] Sidebar sidebar widget
    chosen_town_for_pie = st.sidebar.selectbox('Select a town for injury severity:', ['All'] + list(towns), index=0)
    # [PY3] Function called in two places
    month_data, town_data = choosedata(df, chosen_month, chosen_towns)

    st.write("## Comparing Crash Statistics Between Two Towns")
    compareplots(town_data, chosen_towns)

    st.write("## Crash Frequencies Over Time Across MA")
    map_plot(month_data, chosen_month)

    st.write("## Distribution of Crashes by Collision Description per Month")
    plot_distribution(month_data, chosen_month)

    st.write("## Injury Severity Distribution per Month")
    # [VIZ3] Pie chart
    injurysev_plot(df, chosen_month, chosen_town_for_pie)

if __name__ == "__main__":
    main()
