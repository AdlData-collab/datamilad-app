# datamilad_sql_view_logo.py


import duckdb
import pandas as pd
import os
import streamlit as st
from PIL import Image

st.set_page_config(page_title="DATAMILAD - SQL Viewer", layout="wide")

# --- Chemin absolu du logo ---
script_dir = os.path.dirname(os.path.abspath(__file__))  # dossier du script
logo_path = os.path.join(script_dir, "DATAMILAD.png")
#logo_path = "DATAMILAD.PNG"

# --- Affichage du logo au-dessus du titre ---
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=200)  # Logo au-dessus
else:
    st.write("📌 Logo non trouvé")

# --- Titre de l'application ---
st.title("DATAMILAD - SQL Viewer")

# --- Connexion DuckDB en mémoire ---
conn = duckdb.connect(database=':memory:')

# --- 1️⃣ Upload CSV (optionnel) ---
uploaded_files = st.file_uploader(
    "Choisissez un ou plusieurs fichiers CSV ", 
    type="csv", 
    accept_multiple_files=True
)

def detect_separator(file):
    sample = file.read(2048).decode('utf-8')
    file.seek(0)
    if '\t' in sample:
        return '\t'
    elif ';' in sample:
        return ';'
    else:
        return ','

table_names = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        sep = detect_separator(uploaded_file)
        df = pd.read_csv(uploaded_file, sep=sep)
        table_name = os.path.splitext(uploaded_file.name)[0]
        table_names.append(table_name)
        conn.register(table_name, df)
        st.write(f"✅ Table `{table_name}` créée avec succès")
        st.dataframe(df.head())

# --- 2️⃣ Éditeur SQL ---
st.subheader("Écrire une requête SQL")

default_query = f"SELECT * FROM {table_names[0]} LIMIT 10" if table_names else "SELECT 42 AS demo"
query = st.text_area("Requête SQL :", default_query)

if st.button("Exécuter SQL"):
    try:
        result_df = conn.execute(query).fetchdf()
        st.subheader("Résultat SQL")
        st.dataframe(result_df)

        # --- 3️⃣ Export CSV ---
        csv_data = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Télécharger le résultat SQL en CSV",
            data=csv_data,
            file_name="resultat.csv"
        )

    except Exception as e:
        st.error(f"Erreur SQL : {e}")
