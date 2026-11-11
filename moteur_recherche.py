import streamlit as st
import re
import time
import os

# Configuration de la page
st.set_page_config(
    page_title="Moteur de Recherche Hadoop - UA2",
    page_icon="🔎",
    layout="centered"
)

# --- BARRE LATÉRALE (INFOS DU PROJET) ---
with st.sidebar:
    st.header("🎓 Informations Académiques")
    st.markdown("**Cours :** Base des données massives")
    st.markdown("**Projet :** UA2 — Moteur de recherche distribué")
    st.markdown("---")
    st.subheader("👥 Membres de l'équipe")
    st.write("• **Jehovi Ngalibua**")
    st.write("• **Josué Mutanda**")
    st.markdown("---")
    st.caption("Technologies : Python, Hadoop MapReduce, Hadoop Streaming & HDFS")

# --- EN-TÊTE PRINCIPAL ---
st.title("🔎 Moteur de Recherche Distribué")
st.markdown("**Cours : Base des données massives** | Réalisé par **Jehovi Ngalibua** & **Josué Mutanda**")
st.markdown("---")

# Chargement de l'index inversé en mémoire (Complexité O(1) lors de la recherche)
@st.cache_data
def charger_index(chemin_fichier):
    index = {}
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if "\t" in ligne:
                mot, docs = ligne.split("\t", 1)
                index[mot] = docs.split(",")
    return index

# Trouve automatiquement index_final.txt dans le même dossier que ce script
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_index = os.path.join(dossier_actuel, "index_final.txt")

try:
    debut_chargement = time.perf_counter()
    index_hdfs = charger_index(chemin_index)
    temps_chargement = (time.perf_counter() - debut_chargement) * 1000
    st.success(f"✅ Index inversé chargé en mémoire ({len(index_hdfs):,} mots-clés indexés en {temps_chargement:.2f} ms).")
except FileNotFoundError:
    st.error("❌ Fichier 'index_final.txt' introuvable. Assurez-vous qu'il est dans le même dossier que ce script.")
    st.stop()

# Interface de recherche
requete = st.text_input("Saisissez un ou plusieurs mots-clés :", placeholder="Ex: python, async, error...")

if requete:
    debut_recherche = time.perf_counter()
    # Normalisation identique au Mapper
    mots_cles = re.findall(r'\b[a-zà-ÿ0-9]{2,}\b', requete.lower())
    
    if not mots_cles:
        st.warning("⚠️ Veuillez saisir des mots-clés valides (au moins 2 caractères).")
    else:
        resultats = None
        for mot in mots_cles:
            docs_trouves = set(index_hdfs.get(mot, []))
            resultats = docs_trouves if resultats is None else resultats.intersection(docs_trouves)
        
        temps_recherche_ms = (time.perf_counter() - debut_recherche) * 1000
        
        st.markdown("---")
        if resultats:
            st.subheader(f"📄 {len(resultats)} document(s) trouvé(s)")
            st.info(f"⚡ Temps de réponse via l'index inversé : **{temps_recherche_ms:.4f} ms**")
            for doc in sorted(resultats):
                st.write(f"- `{doc}`")
        else:
            st.error(f"Aucun document ne correspond à la requête : '{requete}' (Recherche effectuée en {temps_recherche_ms:.4f} ms).")

# Pied de page
st.markdown("---")
st.caption("© 2026 — Projet UA2 : Base des données massives | Jehovi Ngalibua & Josué Mutanda")

