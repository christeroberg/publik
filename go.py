import streamlit as st
from openai import OpenAI

# --- 1. Inställningar & Säkerhet ---

# Vi hämtar nyckeln från Streamlit Secrets för att hålla den hemlig
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except:
    st.error("API-nyckel saknas! Lägg till OPENROUTER_API_KEY i Streamlit Cloud Secrets.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

st.set_page_config(page_title="Gissa Ordet", page_icon="🎮")
st.title("🎮 Gissa Ordet: AI-utmaningen")

# Initiera session state (minnet)
if "ledtradar" not in st.session_state:
    st.session_state.ledtradar = []
if "ordet" not in st.session_state:
    st.session_state.ordet = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# --- 2. Funktioner ---

def hamta_ledtradar(antal=5):
    """Försöker hämta ledtrådar från flera olika gratismodeller om en är nere."""
    modeller = [
        "google/gemini-2.0-flash-exp:free",
        "google/learnlm-1.5-pro-experimental:free",
        "mistralai/mistral-7b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]
    
    sista_fel = ""
    
    with st.spinner("AI:n tänker ut ledtrådar..."):
        for modell_namn in modeller:
            try:
                completion = client.chat.completions.create(
                    model=modell_namn,
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                f"Du är en expert på gåtor. Ge {antal} korta poetiska liknelser på svenska. "
                                "VIKTIGT: Du får ABSOLUT INTE nämna det hemliga ordet i ditt svar. "
                                "Skriv INGEN inledande text. Skriv BARA liknelserna, en per rad. "
                                "Varje rad ska börja med 'Som...' eller 'Liknar...'."
                            )
                        },
                        {"role": "user", "content": f"Det hemliga ordet är: {st.session_state.ordet}"}
                    ],
                    timeout=15
                )
                
                svar = completion.choices[0].message.content
                nya_rader = [l.strip() for l in svar.split('\n') if l.strip() and (l.lower().startswith('som') or l.lower().startswith('liknar'))]
                
                if nya_rader:
                    st.session_state.ledtradar.extend(nya_rader)
                    return True # Success!
                    
            except Exception as e:
                sista_fel = str(e)
                continue # Prova nästa modell
        
        st.error(f"Kunde inte hämta ledtrådar. AI-tjänsten är hårt belastad. Fel: {sista_fel}")
        return False

def spara_och_generera_start():
    # Hämtar ordet från text_input via dess key
    nytt_ord = st.session_state.get("input_felt")
    if nytt_ord:
        st.session_state.ordet = nytt_ord.strip()
        hamta_ledtradar(5)

def kontrollera_gissning():
    aktuell_gissning = st.session_state.gissnings_ruta.strip().lower()
    if aktuell_gissning:
        if aktuell_gissning == st.session_state.ordet.lower():
            st.session_state.feedback = "correct"
        else:
            st.session_state.feedback = "wrong"
        # Tömmer rutan för nästa gissning
        st.session_state.gissnings_ruta = ""

# --- 3. UI / Logik ---

# Steg 1: Mata in det hemliga ordet
if not st.session_state.ordet:
    st.info("Börja med att välja ett ord som någon annan ska gissa på.")
    st.text_input(
        "Skriv det hemliga ordet och tryck ENTER:", 
        key="input_felt",
        on_change=spara_och_generera_start,
        #type="password", # Döljer ordet medan man skriver
        placeholder="T.ex. Sommarstuga"
    )
else:
    # Steg 2: Visa spelet
    st.success(f"✅ Ordet är dolt! Det finns nu {len(st.session_state.ledtradar)} ledtrådar.")
    
    if st.session_state.ledtradar:
        st.divider()
        for i, l in enumerate(st.session_state.ledtradar, 1):
            st.info(f"Ledtråd {i}: {l}")
        
        if st.button("Visa 5 ledtrådar till"):
            hamta_ledtradar(5)
            st.rerun()

        st.divider()
        
        st.text_input(
            "Vad tror du det hemliga ordet är?", 
            key="gissnings_ruta", 
            on_change=kontrollera_gissning
        )
        
        if st.session_state.feedback == "correct":
            st.balloons()
            st.success(f"🎉 RÄTT GISSAT! Ordet var: {st.session_state.ordet}")
        elif st.session_state.feedback == "wrong":
            st.warning("Fel! Försök igen eller be om fler ledtrådar.")

# Sidomeny för nollställning
st.sidebar.title("Inställningar")
if st.sidebar.button("Nollställ och börja om"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
