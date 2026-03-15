import streamlit as st
from openai import OpenAI

# --- 1. Inställningar & Säkerhet ---

# Kontrollera att API-nyckeln finns i Streamlit Secrets
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Nyckeln saknas i Streamlit Cloud Secrets!")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

st.set_page_config(page_title="Imposter utmaningen", page_icon="🎮")

# --- 2. Session State (Minne) ---
if "hemligt_ord" not in st.session_state:
    st.session_state.hemligt_ord = ""
if "ledtradar" not in st.session_state:
    st.session_state.ledtradar = []

# --- 3. Funktion för att hämta ledtrådar (Robust) ---
def hamta_ledtradar(ordet, antal=5):
    # Lista på modeller som faktiskt existerar och ofta är gratis/stabila
    modeller = [
        "google/gemini-2.0-flash-exp:free",
        "google/learnlm-1.5-pro-experimental:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/mistral-7b-instruct:free"
    ]
    
    sista_fel = ""
    for m in modeller:
        try:
            res = client.chat.completions.create(
                model=m,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Du är en expert på gåtor. Skriv {antal} korta poetiska ledtrådar på svenska som börjar med 'Som...' eller 'Liknar...'. En per rad. Nämn ABSOLUT INTE ordet '{ordet}' i ditt svar."
                    },
                    {"role": "user", "content": f"Ge mig ledtrådar för ordet: {ordet}"}
                ],
                timeout=15
            )
            # Rensa och filtrera rader
            rader = [r.strip() for r in res.choices[0].message.content.split('\n') if len(r.strip()) > 3]
            if rader:
                return rader
        except Exception as e:
            sista_fel = str(e)
            continue
    
    st.error(f"AI-tjänsten är överbelastad just nu. Försök igen om en minut. (Fel: {sista_fel})")
    return []

# --- 4. UI / LOGIK ---

# --- STEG 1: STARTA (Visa titeln "Imposter utmaningen" här) ---
if not st.session_state.hemligt_ord:
    st.title("🕵️ Imposter utmaningen")
    st.info("Börja med att välja ett ord som någon annan ska gissa på.")
    
    with st.form("setup", clear_on_submit=True):
        # type="default" gör att webbläsaren inte föreslår lösenord
        valt_ord = st.text_input("Välj ett hemligt ord:", placeholder="T.ex. Banan")
        skicka = st.form_submit_button("Starta spelet")
        
        if skicka and valt_ord:
            st.session_state.hemligt_ord = valt_ord.strip().lower()
            with st.spinner("AI-agenten skapar ledtrådar..."):
                nya_ledtradar = hamta_ledtradar(st.session_state.hemligt_ord)
                if nya_ledtradar:
                    st.session_state.ledtradar = nya_ledtradar
                    st.rerun()
                else:
                    # Nollställ om det misslyckades så man kan försöka igen
                    st.session_state.hemligt_ord = ""

# --- STEG 2: SPELA ---
else:
    st.title("🎮 Gissa Ordet")
    st.success(f"✅ Ordet är dolt! Det finns {len(st.session_state.ledtradar)} ledtrådar.")
    
    # Visa befintliga ledtrådar
    for i, ledtrad in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {ledtrad}")

    # Knapp för fler ledtrådar
    if st.button("Hämta 5 ledtrådar till"):
        with st.spinner("Hämtar fler..."):
            fler = hamta_ledtradar(st.session_state.hemligt_ord)
            if fler:
                st.session_state.ledtradar.extend(fler)
                st.rerun()

    st.divider()

    # Gissningsfältet
    with st.form("guess_form", clear_on_submit=True):
        gissning = st.text_input("Vad är det för ord?")
        if st.form_submit_button("Gissa!"):
            if gissning.lower() == st.session_state.hemligt_ord:
                st.balloons()
                st.success(f"🎉 RÄTT! Ordet var: {st.session_state.hemligt_ord.upper()}")
            else:
                st.error("Fel gissat, försök igen!")

# Sidomeny för kontroll
st.sidebar.title("Inställningar")
if st.sidebar.button("Nollställ och börja om"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
