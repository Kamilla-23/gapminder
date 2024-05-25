import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Gapminder')

st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")

@st.cache_data
def load_and_preprocess_data():
    # Load the data
    population = pd.read_csv('pop.csv')
    life_expectancy = pd.read_csv('lex.csv')
    gni_per_capita = pd.read_csv('ny_gnp_pcap_pp_cd.csv')

    # Forward fill missing values
    population.ffill(inplace=True)
    life_expectancy.ffill(inplace=True)
    gni_per_capita.ffill(inplace=True)

    # Convert year columns to numeric
    population.columns = ['country'] + [int(col) if col != 'country' else col for col in population.columns[1:]]
    life_expectancy.columns = ['country'] + [int(col) if col != 'country' else col for col in life_expectancy.columns[1:]]
    gni_per_capita.columns = ['country'] + [int(col) if col != 'country' else col for col in gni_per_capita.columns[1:]]

    # Tidy the data
    population = population.melt(id_vars=["country"], var_name="year", value_name="population")
    life_expectancy = life_expectancy.melt(id_vars=["country"], var_name="year", value_name="life_expectancy")
    gni_per_capita = gni_per_capita.melt(id_vars=["country"], var_name="year", value_name="gni_per_capita")

    # Convert 'k' values to numeric for GNI per capita
    def convert_to_numeric(value):
        if 'k' in str(value):
            return float(value.replace('k', '')) * 1000
        else:
            return float(value)

    gni_per_capita['gni_per_capita'] = gni_per_capita['gni_per_capita'].apply(convert_to_numeric)

    # Convert values to numeric types
    population['year'] = pd.to_numeric(population['year'])
    population['population'] = pd.to_numeric(population['population'], errors='coerce')

    life_expectancy['year'] = pd.to_numeric(life_expectancy['year'])
    life_expectancy['life_expectancy'] = pd.to_numeric(life_expectancy['life_expectancy'], errors='coerce')

    gni_per_capita['year'] = pd.to_numeric(gni_per_capita['year'])
    gni_per_capita['gni_per_capita'] = pd.to_numeric(gni_per_capita['gni_per_capita'], errors='coerce')

    # Merge dataframes
    df = pd.merge(population, life_expectancy, on=["country", "year"])
    df = pd.merge(df, gni_per_capita, on=["country", "year"])

    # Handle any remaining missing values after merging
    df.ffill(inplace=True)
    df.dropna(subset=['population', 'life_expectancy', 'gni_per_capita'], inplace=True)

    return df

# Load data
df = load_and_preprocess_data()

# Year slider
year = st.slider('Year', int(df['year'].min()), int(df['year'].max()), step=1)

# Multiselect widget for countries
countries = st.multiselect('Select Countries', df['country'].unique(), default=df['country'].unique())

# Filter dataframe based on selections
filtered_df = df[(df['year'] == year) & (df['country'].isin(countries))]

# Bubble chart
fig = px.scatter(
    filtered_df, 
    x='gni_per_capita', 
    y='life_expectancy',
    size='population', 
    color='country', 
    hover_name='country',
    log_x=False, 
    size_max=10, 
    title=f'Gapminder Data for {year}'
)

# Set a constant max x value for better comparison
fig.update_layout(xaxis=dict(range=[0, 110000]))

st.plotly_chart(fig)