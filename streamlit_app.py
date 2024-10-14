import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import os

# Set page configuration with white background
st.set_page_config(page_title="Bundestagswahlprogramme Analyse", layout="wide")

# Set custom CSS for white background and removing the black background issue
st.markdown(
    """
    <style>
    body {
        background-color: white;
        color: black;
    }
    .css-18e3th9 {
        background-color: white !important;
    }
    .css-1d391kg {
        background-color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Laden der vorverarbeiteten CSV-Datei mit Caching
@st.cache_data
def load_data():
    return pd.read_csv("wahlprogramme_analysis.csv")

df = load_data()

# Dynamisch die verfügbaren Jahre ermitteln
available_years = sorted(df['Jahr'].unique(), reverse=True)

# Dynamischer Titel basierend auf den verfügbaren Jahren
st.title(f"Analyse der Bundestagswahlprogramme ({', '.join(map(str, sorted(available_years)))})")

# Erklärungstext zur Analyse
st.markdown("""
    Diese Analyse basiert auf den Wahlprogrammen der wichtigsten deutschen Parteien für die Jahre 2013, 2017 und 2021. 
    Dabei werden die häufigsten Wörter in den Wahlprogrammen gezählt, wobei häufig vorkommende und wenig aussagekräftige Stopwörter (wie "und", "der", "die") automatisch herausgefiltert werden. 
    In den folgenden Grafiken könnt ihr die Häufigkeit eines bestimmten Wortes über die Jahre hinweg vergleichen.
""")

# Farben der Parteien
party_colors = {
    "CDU_CSU": "black",
    "SPD": "red",
    "AfD": "blue",
    "Bündnis90_DieGrünen": "green",
    "DIE LINKE": "violet",
    "FDP": "yellow"
}

# Suchleiste
search_word = st.text_input("Suche nach einem Wort:", "").strip().lower()

# Diagramm erstellen, falls ein Wort eingegeben wurde
if search_word:
    # Filtere die Daten für das gesuchte Wort
    filtered_df = df[df['Wort'] == search_word]

    if filtered_df.empty:
        st.warning(f"Das Wort '{search_word}' wurde in den Wahlprogrammen nicht gefunden.")
    else:
        # Daten für das Diagramm sammeln
        data = []
        parties = filtered_df["Partei"].unique()

        for party in parties:
            party_data = filtered_df[filtered_df["Partei"] == party]
            trace = go.Scatter(
                x=party_data["Jahr"],
                y=party_data["Vorkommen"],
                mode='lines+markers',
                name=party,
                line=dict(color=party_colors.get(party, "gray")),
                marker=dict(size=8),
                hovertemplate=(
                    '<b>%{text}</b><br>' +
                    'Jahr: %{x}<br>' +
                    'Häufigkeit: %{y}<br>' +
                    'Rang: %{customdata}<extra></extra>'
                ),
                text=[party]*len(party_data),
                customdata=party_data["Rang"]
            )
            data.append(trace)

        # Layout mit transparentem Diagrammhintergrund und "Häufigkeit" als Achsentitel
        layout = go.Layout(
            title=f"Häufigkeit des Wortes '{search_word}' in den Wahlprogrammen",
            xaxis=dict(title='Jahr', tickmode='array', tickvals=sorted(df['Jahr'].unique())),  # Responsive Jahre anzeigen
            yaxis=dict(title='Häufigkeit'),
            plot_bgcolor='rgba(0,0,0,0)',  # Transparenter Hintergrund
            hovermode='closest'
        )

        fig = go.Figure(data=data, layout=layout)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Bitte gebt ein Wort in die Suchleiste ein, um die Analyse zu starten.")

# Füge einen Abstand ein
st.markdown("<br><br>", unsafe_allow_html=True)

# Neuer Abschnitt für Dropdown und Tabellen
st.subheader("Top 20 Wörter pro Jahr und Partei")

# Erklärungstext zu den Top 20 Wörtern
st.markdown("""
    In dieser Tabelle seht ihr die 20 häufigsten Wörter in den Wahlprogrammen der Parteien für das ausgewählte Jahr. 
    Die Wörter sind nach ihrer Häufigkeit im jeweiligen Wahlprogramm sortiert, wobei auch die Rangposition und die Anzahl der Vorkommnisse angegeben sind.
""")

# Dropdown-Menü für die Auswahl des Jahres (mit dem neuesten Jahr als Standard)
selected_year = st.selectbox("Wähle ein Jahr:", available_years, index=0)

# Tabelle der Top 20 Wörter für das ausgewählte Jahr anzeigen
st.subheader(f"Top 20 Wörter im Jahr {selected_year}")

# Filtere die Daten für das ausgewählte Jahr
year_df = df[df['Jahr'] == selected_year]

# Für jede Partei die Top 20 Wörter finden und den Index als Rang setzen
top_words_data = {}
for party in party_colors.keys():
    party_df = year_df[year_df['Partei'] == party].sort_values(by="Vorkommen", ascending=False).head(20)
    # Setze den Index neu und lasse ihn bei 1 beginnen
    party_df.reset_index(drop=True, inplace=True)
    party_df.index += 1  # Der Index beginnt nun bei 1
    # "Vorkommen" wird in "Häufigkeit" umbenannt
    party_df.rename(columns={"Vorkommen": "Häufigkeit"}, inplace=True)
    top_words_data[party] = party_df[['Wort', 'Häufigkeit']]

# Eine Tabelle mit den Top 20 Wörtern für jede Partei erstellen
st.write("**Top 20 Wörter pro Partei:**")

# Anzahl der Spalten in einer Reihe festlegen (z.B. 3 Tabellen nebeneinander)
cols = st.columns(3)

# Zeige die Tabellen für jede Partei an, verteilt auf die Spalten
for idx, (party, data) in enumerate(top_words_data.items()):
    col = cols[idx % 3]  # Verteilt die Tabellen auf 3 Spalten
    col.write(f"**{party}:**")
    # Zeige die Tabelle mit dem Index als Rang
    col.table(data)