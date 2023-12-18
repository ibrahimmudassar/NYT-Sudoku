import plotly.express as px
import pandas as pd

df = pd.read_csv("historical_analysis/historical_nyt_sudokus.csv")
df['print_date'] = pd.to_datetime(df['print_date'], format='%Y-%m-%d')
df.sort_values(by='print_date', inplace=True)

# fig = px.line(df, x="print_date", y="HoDoKu", color='difficulty')
fig = px.box(df, x='day_of_week', y="HoDoKu", color='difficulty', hover_data=['HoDoKu'])
fig.update_layout(xaxis={"categoryorder": "array", "categoryarray": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]})
fig.show()