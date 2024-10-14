import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Set page configuration with white background
st.set_page_config(page_title="Bundestagswahlprogramme Analyse", layout="wide")
st.title("Analyse der Bundestagswahlprogramme")

# Set custom CSS for white background and chart style
st.markdown(
    """
    <style>
    body {
        background-color: white !important;
        color: black !important;
    }
    .css-18e3th9 {
        background-color: white !important;
        color: black !important;
    }
    .css-1d391kg {
        background-color: white !important;
        color: black !important;
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
available_years = sorted(df['Jahr'].unique())

# Farben der Parteien definieren
party_colors = {
    "CDU_CSU": "black",
    "SPD": "red",
    "AfD": "blue",
    "Bündnis90_DieGrünen": "green",
    "DIE LINKE": "violet",
    "FDP": "yellow"
}

# Erklärungstext zur Analyse mit dynamischer Angabe der Jahre
st.markdown(f"""
    Diese Analyse basiert auf den Wahlprogrammen der wichtigsten deutschen Parteien für die Jahre {', '.join(map(str, available_years))}. 
    Dabei werden die häufigsten Wörter in den Wahlprogrammen gezählt, wobei häufig vorkommende und wenig aussagekräftige Stopwörter 
    (wie "und", "der", "die") automatisch herausgefiltert werden. In den folgenden Grafiken könnt ihr die Häufigkeit 
    eines bestimmten Wortes über die Jahre hinweg vergleichen.
""")

# Eingabe für das Wort
search_word = st.text_input("Gib ein Wort ein und drücke Enter:", key="search_word").strip().lower()

# Wenn ein Wort eingegeben wurde, zeige die Analyse
if search_word:
    st.subheader(f"Analyse des Wortes: {search_word}")

    # Daten für das Diagramm sammeln
    data = []
    parties = df["Partei"].unique()

    for party in parties:
        party_data = df[df["Partei"] == party]
        occurrences = []
        hover_info = []

        for year in sorted(party_data["Jahr"].unique()):
            yearly_data = party_data[party_data["Jahr"] == year]
            word_data = yearly_data[yearly_data["Wort"] == search_word]
            if not word_data.empty:
                occurrences.append(word_data["Vorkommen"].values[0])
                hover_info.append(f"{search_word}: {word_data['Vorkommen'].values[0]} (Rang: {word_data['Rang'].values[0]})")
            else:
                occurrences.append(0)
                hover_info.append(f"{search_word}: nicht vorhanden")

        # Erstelle die Daten für die Darstellung in der Chart
        trace = go.Scatter(
            x=sorted(party_data["Jahr"].unique()),
            y=occurrences,
            mode='lines+markers',
            name=party,
            line=dict(color=party_colors.get(party, "gray")),
            marker=dict(size=8),
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Jahr: %{x}<br>' +
                'Häufigkeit: %{y}<br>' +
                '%{customdata}<extra></extra>'
            ),
            text=[party]*len(occurrences),
            customdata=hover_info
        )
        data.append(trace)

    # Layout mit transparentem Diagrammhintergrund und "Häufigkeit" als Achsentitel
    layout = go.Layout(
        title=f"Häufigkeit des Wortes '{search_word}'",
        xaxis=dict(title='Jahr', tickmode='array', tickvals=sorted(df['Jahr'].unique())),  # Responsive Jahre anzeigen
        yaxis=dict(title='Häufigkeit'),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparenter Hintergrund
        hovermode='closest'
    )

    # Chart darstellen
    fig = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

# Abschnitt für die Tabellen
st.subheader("Top 20 Wörter pro Jahr und Partei")

# Erklärungstext zu den Top 20 Wörtern
st.markdown(f"""
    In dieser Tabelle seht ihr die 20 häufigsten Wörter in den Wahlprogrammen der Parteien für die Jahre {', '.join(map(str, available_years))}. 
    Die Wörter sind nach ihrer Häufigkeit im jeweiligen Wahlprogramm sortiert, wobei auch die Rangposition und die Anzahl der Vorkommnisse angegeben sind.
""")

# Dropdown-Menü für die Auswahl des Jahres (mit dem neuesten Jahr als Standard)
selected_year = st.selectbox("Wähle ein Jahr:", available_years, index=len(available_years)-1)

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