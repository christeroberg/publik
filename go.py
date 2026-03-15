import streamlit as st
from openai import OpenAI

# --- 1. Inställningar & Säkerhet ---

if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Nyckeln saknas i Streamlit Cloud Secrets!")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

st.set_page_config(page_title="Imposter utmaningen", page_icon="🕵️")

# --- 2. Session State ---
if "hemligt_ord" not in st.session_state:
    st.session_state.hemligt_ord = ""
if "ledtradar" not in st.session_state:
    st.session_state.ledtradar = []

# --- 3. Funktion för att hämta ledtrådar ---
def hamta_ledtradar(ordet, antal=5):
    # Vi prioriterar Gemini som är stabilast för gratisanvändare just nu
    modeller = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "openrouter/auto" # Låter OpenRouter välja om de andra fallerar
    ]
    
    sista_fel = ""
    for m in modeller:
        try:
            res = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content": f"Skriv {antal} korta ledtrådar på svenska om '{ordet}'. En per rad. Börja varje rad med 'Som...' eller 'Liknar...'. Nämn aldrig själva ordet."},
                    {"role": "user", "content": f"Ge mig ledtrådar."}
                ],
                timeout=15
            )
            rader = [r.strip() for r in res.choices[0].message.content.split('\n') if len(r.strip()) > 2]
            if rader:
                return rader
        except Exception as e:
            sista_fel = str(e)
            continue
    
    st.error(f"Kunde inte hämta svar. Kontrollera din API-nyckel i Secrets! (Fel: {sista_fel})")
    return []

# --- 4. UI ---

if not st.session_state.hemligt_ord:
    # Vi använder st.header istället för st.title för att få plats på en rad
    st.header("🕵️ Imposter utmaningen: Gissa ordet")
    st.info("Välj ett ord som din kompis ska gissa på.")
    
    with st.form("setup"):
        valt_ord = st.text_input("Välj ett hemligt ord:", placeholder="T.ex. Kaffekopp")
        if st.form_submit_button("Starta spelet") and valt_ord:
            st.session_state.hemligt_ord = valt_ord.strip().lower()
            with st.spinner("AI-agenten skapar ledtrådar..."):
                nya = hamta_ledtradar(st.session_state.hemligt_ord)
                if nya:
                    st.session_state.ledtradar = nya
                    st.rerun()
                else:
                    st.session_state.hemligt_ord = ""
else:
    st.header("🎮 Gissa Ordet")
    for i, ledtrad in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {ledtrad}")

    if st.button("Hämta fler ledtrådar"):
        with st.spinner("Hämtar..."):
            fler = hamta_ledtradar(st.session_state.hemligt_ord)
            if fler:
                st.session_state.ledtradar.extend(fler)
                st.rerun()

    with st.form("guess"):
        gissning = st.text_input("Din gissning:")
        if st.form_submit_button("Gissa!"):
            if gissning.lower() == st.session_state.hemligt_ord:
                st.balloons()
                st.success("🎉 Rätt gissat!")
            else:
                st.error("Tyvärr fel, försök igen!")

if st.sidebar.button("Nollställ spelet"):
    st.session_state.clear()
    st.rerun()
