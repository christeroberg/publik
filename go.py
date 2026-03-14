import streamlit as st
from openai import OpenAI

# 1. Inställningar
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

st.set_page_config(page_title="Gissa Ordet", page_icon="🎮")
st.title("🎮 Gissa Ordet: AI-utmaningen")

# Initiera minnet
if "ledtradar" not in st.session_state:
    st.session_state.ledtradar = []
if "ordet" not in st.session_state:
    st.session_state.ordet = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# --- FUNKTIONER ---

def hamta_ledtradar(antal=5):
    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"Du är en expert på gåtor. Ge {antal} korta poetiska liknelser på svenska. "
                        "VIKTIGT: Du får ABSOLUT INTE nämna det hemliga ordet i ditt svar. "
                        "Skriv INGEN inledande text, ingen hälsning och ingen avslutning. "
                        "Skriv BARA liknelserna, en per rad. Varje rad ska börja med 'Som...' eller 'Liknar...'."
                    )
                },
                {"role": "user", "content": f"Det hemliga ordet är: {st.session_state.ordet}"}
            ]
        )
        svar = completion.choices[0].message.content
        # Vi rensar bort eventuellt skräp som AI:n ändå lyckats skriva
        nya_rader = [l.strip() for l in svar.split('\n') if l.strip() and (l.lower().startswith('som') or l.lower().startswith('liknar'))]
        st.session_state.ledtradar.extend(nya_rader)
    except Exception as e:
        st.error(f"Kunde inte hämta ledtrådar: {e}")
        
def spara_och_generera_start():
    if st.session_state.input_felt:
        st.session_state.ordet = st.session_state.input_felt
        hamta_ledtradar(5)

def kontrollera_gissning():
    # Hämtar gissningen från session_state (pga key="gissnings_ruta")
    aktuell_gissning = st.session_state.gissnings_ruta.strip().lower()
    
    if aktuell_gissning:
        if aktuell_gissning == st.session_state.ordet.lower():
            st.session_state.feedback = "correct"
        else:
            st.session_state.feedback = "wrong"
        
        # VIKTIGT: Här tömmer vi gissningsrutan direkt
        st.session_state.gissnings_ruta = ""

# --- UI / LOGIK ---

# 2. Inmatning av hemligt ord
if not st.session_state.ordet:
    st.text_input(
        "Skriv det hemliga ordet och tryck ENTER:", 
        key="input_felt",
        on_change=spara_och_generera_start,
        placeholder="Skriv ordet här..."
    )
else:
    st.success(f"✅ Ordet är dolt! Det finns nu {len(st.session_state.ledtradar)} ledtrådar.")

# 3. Visa ledtrådar och gissningsdel
if st.session_state.ledtradar:
    st.divider()
    for i, l in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {l}")
    
    if st.button("Visa 5 ledtrådar till"):
        hamta_ledtradar(5)
        st.rerun()

    st.divider()
    
    # Gissningsfältet med automatisk rensning via on_change
    st.text_input(
        "Vad tror du det hemliga ordet är?", 
        key="gissnings_ruta", 
        on_change=kontrollera_gissning
    )
    
    # Visa feedback baserat på senaste gissningen
    if st.session_state.feedback == "correct":
        st.balloons()
        st.success("🎉 RÄTT GISSAT!")
    elif st.session_state.feedback == "wrong":
        st.warning("Fel! Försök igen.")

# Starta om
st.sidebar.divider()
if st.sidebar.button("Nollställ och börja om"):
    st.session_state.clear()
    st.rerun()