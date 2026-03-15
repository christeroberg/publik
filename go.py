import streamlit as st
from openai import OpenAI

# --- 1. Inställningar ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Nyckeln saknas i Streamlit Cloud Secrets!")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

st.set_page_config(page_title="Imposter utmaningen", page_icon="🕵️")

if "hemligt_ord" not in st.session_state:
    st.session_state.hemligt_ord = ""
if "ledtradar" not in st.session_state:
    st.session_state.ledtradar = []

# --- 2. Funktion för att hämta ledtrådar ---
def hamta_ledtradar(ordet, antal=5):
    try:
        res = client.chat.completions.create(
            model="openai/gpt-4o-mini", # Nu använder vi en av de bästa modellerna!
            messages=[
                {"role": "system", "content": "Du är en expert på gåtor. Skriv korta, poetiska ledtrådar på svenska. Börja varje rad med 'Som...' eller 'Liknar...'. Nämn aldrig själva ordet."},
                {"role": "user", "content": f"Ge mig {antal} ledtrådar för ordet: {ordet}"}
            ]
        )
        rader = res.choices[0].message.content.strip().split('\n')
        return [r.strip() for r in rader if len(r) > 2]
    except Exception as e:
        st.error(f"Fel vid hämtning: {e}")
        return []

# --- 3. UI ---
if not st.session_state.hemligt_ord:
    # Rubrik på en rad
    st.subheader("🕵️ Imposter utmaningen: Gissa ordet!")
    
    with st.form("setup"):
        valt_ord = st.text_input("Välj ett hemligt ord:", placeholder="T.ex. Sommarstuga")
        if st.form_submit_button("Starta spelet") and valt_ord:
            st.session_state.hemligt_ord = valt_ord.strip().lower()
            with st.spinner("AI-agenten tänker ut ledtrådar..."):
                st.session_state.ledtradar = hamta_ledtradar(st.session_state.hemligt_ord)
                st.rerun()
else:
    st.subheader("🎮 Gissa Ordet")
    for i, ledtrad in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {ledtrad}")

    with st.form("guess"):
        gissning = st.text_input("Din gissning:")
        if st.form_submit_button("Gissa!"):
            if gissning.lower() == st.session_state.hemligt_ord:
                st.balloons()
                st.success(f"🎉 RÄTT! Ordet var: {st.session_state.hemligt_ord.upper()}")
            else:
                st.error("Fel gissat, försök igen!")

if st.sidebar.button("Börja om"):
    st.session_state.clear()
    st.rerun()
