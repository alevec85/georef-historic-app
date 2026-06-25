import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image

# 1. Configurazione della pagina
st.set_page_config(page_title="GeoRef Historic", layout="wide", initial_sidebar_state="expanded")

# 2. Inizializzazione Session State per la gestione "Multilivello"
if 'immagini_caricate' not in st.session_state:
    # Creiamo un dizionario vuoto per immagazzinare i file
    st.session_state['immagini_caricate'] = {} 
if 'immagine_selezionata' not in st.session_state:
    st.session_state['immagine_selezionata'] = None

# --- BARRA LATERALE (SIDEBAR) ---
with st.sidebar:
    st.header("🗂️ Pannello di Controllo")
    st.markdown("Gestione batch immagini storiche")
    
    # Caricamento multiplo abilitato (accept_multiple_files=True)
    uploaded_files = st.file_uploader(
        "Carica scansioni (Multiplo consentito)", 
        type=["jpg", "jpeg", "png", "tif"], 
        accept_multiple_files=True
    )
    
    # Se vengono caricati file, li salviamo nella memoria di sessione
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state['immagini_caricate']:
                img_pil = Image.open(file)
                # Salviamo un dizionario con i metadati per ogni immagine
                st.session_state['immagini_caricate'][file.name] = {
                    'image': img_pil,
                    'size': img_pil.size,
                    'status': 'In attesa' # In futuro qui salveremo se è georeferenziata o no
                }
    
    st.divider()
    
    # Lista delle immagini caricate
    if st.session_state['immagini_caricate']:
        st.subheader("Elenco Livelli")
        nomi_file = list(st.session_state['immagini_caricate'].keys())
        
        # Menu a tendina per scegliere quale immagine visualizzare/elaborare
        st.session_state['immagine_selezionata'] = st.selectbox(
            "Immagine Attiva:", 
            nomi_file
        )
        
        # Mostra dettagli dell'immagine attiva
        img_attiva = st.session_state['immagini_caricate'][st.session_state['immagine_selezionata']]
        st.caption(f"Dimensioni: {img_attiva['size'][0]} x {img_attiva['size'][1]} px")
        st.caption(f"Stato: {img_attiva['status']}")
        
        # Tasto per lo svuotamento della cache
        if st.button("Svuota lista", use_container_width=True):
            st.session_state['immagini_caricate'] = {}
            st.session_state['immagine_selezionata'] = None
            st.rerun()
    else:
        st.info("Nessuna immagine caricata.")

# --- CORPO PRINCIPALE ---
st.title("🛰️ GeoRef Historic Imagery - Workspace")
col_img, col_map = st.columns([1, 1]) # Proporzione colonne 50/50

with col_img:
    st.subheader("1. Immagine Storica")
    # Mostriamo solo l'immagine che l'utente ha selezionato nella sidebar
    if st.session_state['immagine_selezionata']:
        nome_file = st.session_state['immagine_selezionata']
        img_da_mostrare = st.session_state['immagini_caricate'][nome_file]['image']
        st.image(img_da_mostrare, caption=f"In elaborazione: {nome_file}", use_container_width=True)
    else:
        st.info("Carica le tue immagini nel pannello laterale a sinistra per iniziare.")

with col_map:
    st.subheader("2. Mappa di Riferimento")
    
    wms_url = st.text_input("URL WMS", placeholder="Inserisci GetMap URL")
    layer_name = st.text_input("Nome Layer", placeholder="es. ortofoto")
    
    m = folium.Map(location=[40.6285, 16.9405], zoom_start=14)
    
    if wms_url and layer_name:
        folium.WmsTileLayer(
            url=wms_url,
            layers=layer_name,
            transparent=True,
            control=True,
            fmt="image/png",
        ).add_to(m)
        folium.LayerControl().add_to(m)

    st_folium(m, width=700, height=500, key="map")