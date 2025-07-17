import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# from wordcloud import WordCloud

# Streamlit Page Configuration
st.set_page_config(page_title="Netflix Data Analysis", layout="wide")

# Title
st.title("🎬 Netflix Data Cleaning, Analysis & Visualization")
st.caption("Project by **Mayuri Dandekar** | Powered by Streamlit & Python")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("netflix1.csv")
    return df

data = load_data()
st.subheader("🔍 Raw Dataset Preview")
st.dataframe(data.head())

# Data Cleaning
st.subheader("🧹 Data Cleaning")

# Drop duplicates
data.drop_duplicates(inplace=True)

# Convert 'date_added' to datetime
data['date_added'] = pd.to_datetime(data['date_added'], errors='coerce')

# Handle missing values safely
for col in ['director', 'country']:
    if col in data.columns:
        data[col] = data[col].fillna("Not Given")

# Extract year and month
data['year_added'] = data['date_added'].dt.year
data['month_added'] = data['date_added'].dt.month

st.success("✅ Data cleaned: Duplicates removed, nulls handled, dates converted.")

# Sidebar Filters
st.sidebar.header("📊 Filters")
content_type = st.sidebar.multiselect("Select Content Type", options=data['type'].unique(), default=data['type'].unique())

filtered_data = data[data['type'].isin(content_type)]

# Visualization 1: Movies vs TV Shows
st.subheader("🎭 Content Distribution: Movies vs TV Shows")
type_counts = filtered_data['type'].value_counts()

fig1, ax1 = plt.subplots(1, 2, figsize=(12, 4))
sns.barplot(x=type_counts.index, y=type_counts.values, ax=ax1[0], palette='Set2')
ax1[0].set_title("Content Count")
ax1[0].set_ylabel("Count")

ax1[1].pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set2'))
ax1[1].axis('equal')
ax1[1].set_title("Content Share")

st.pyplot(fig1)

# Show cleaned data if toggled
if st.checkbox("Show Cleaned Dataset"):
    st.dataframe(filtered_data)

# Genre Analysis
st.subheader("🎬 Top 10 Most Common Genres on Netflix")

# Safely split 'listed_in' column and explode it
if 'listed_in' in filtered_data.columns:
    filtered_data['genres'] = filtered_data['listed_in'].apply(lambda x: [genre.strip() for genre in x.split(',')])
    exploded_genres = filtered_data.explode('genres')
    
    top_genres = exploded_genres['genres'].value_counts().head(10)

    # Plotting
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_genres.values, y=top_genres.index, palette="viridis", ax=ax2)
    ax2.set_title("Top 10 Genres on Netflix")
    ax2.set_xlabel("Count")
    ax2.set_ylabel("Genre")
    st.pyplot(fig2)
else:
    st.warning("⚠️ 'listed_in' column not found.")


# Yearly Trend
st.subheader("📈 Yearly Releases of Movies & TV Shows")

yearly_data = filtered_data.groupby(['year_added', 'type']).size().unstack().fillna(0)

fig3, ax3 = plt.subplots(figsize=(12, 5))
yearly_data.plot(kind='line', marker='o', ax=ax3)
plt.xticks(rotation=45)
ax3.set_ylabel("Number of Releases")
ax3.set_title("Content Added to Netflix by Year")
st.pyplot(fig3)

# Monthly Trend
st.subheader("📅 Monthly Trend of Releases")

monthly_data = filtered_data.groupby(['month_added', 'type']).size().unstack().fillna(0).sort_index()

fig4, ax4 = plt.subplots(figsize=(12, 5))
monthly_data.plot(kind='bar', ax=ax4)
plt.xticks(rotation=0)
ax4.set_xlabel("Month")
ax4.set_ylabel("Number of Releases")
ax4.set_title("Monthly Releases of Movies and TV Shows")
st.pyplot(fig4)


# Word Cloud for Movie Titles
st.subheader("☁️ Word Cloud of Netflix Titles")

from wordcloud import WordCloud

# Combine titles into one string
all_titles = " ".join(filtered_data['title'].dropna())

# Generate word cloud
wordcloud = WordCloud(width=1000, height=400, background_color='black', colormap='Pastel1').generate(all_titles)

fig5, ax5 = plt.subplots(figsize=(12, 6))
ax5.imshow(wordcloud, interpolation='bilinear')
ax5.axis('off')
st.pyplot(fig5)

# Download Button
st.download_button(
    label="⬇️ Download Cleaned Data as CSV",
    data=filtered_data.to_csv(index=False),
    file_name="cleaned_netflix_data.csv",
    mime="text/csv"
)
