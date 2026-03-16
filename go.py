import streamlit as st
from openai import OpenAI

# --- 1. Inställningar ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Nyckeln saknas i Streamlit Cloud Secrets!")
    st.stop()
else :
    st.text_input("Key exist")
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
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Du är en expert på gåtor. Skriv exakt {antal} korta, poetiska ledtrådar på svenska. Varje ledtråd på en ny rad. Börja varje rad med 'Som...' eller 'Liknar...'. Nämn aldrig ordet '{ordet}'."},
                {"role": "user", "content": f"Ge mig {antal} ledtrådar för mitt hemliga ord."}
            ]
        )
        # Dela upp svaret i rader, rensa tomma rader och ta bara de första 5 (ifall AI:n skriver för mycket)
        rader = [r.strip() for r in res.choices[0].message.content.strip().split('\n') if len(r.strip()) > 2]
        return rader[:antal] 
    except Exception as e:
        st.error(f"Fel vid hämtning: {e}")
        return []

# --- 3. UI ---
if not st.session_state.hemligt_ord:
    st.subheader("🕵️ Imposter utmaningen: Gissa ordet!")
    
    with st.form("setup"):
        valt_ord = st.text_input("Välj ett hemligt ord:", placeholder="T.ex. Sommarstuga", "OBS! Endast ETT ord")
        if st.form_submit_button("Starta spelet") and valt_ord:
            st.session_state.hemligt_ord = valt_ord.strip().lower()
            with st.spinner("AI-agenten tänker ut ledtrådar..."):
                # Hämtar de första 5
                st.session_state.ledtradar = hamta_ledtradar(st.session_state.hemligt_ord)
                st.rerun()
else:
    st.subheader("🎮 Gissa Ordet")
    
    # Visa alla ledtrådar som finns i listan
    for i, ledtrad in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {ledtrad}")

    # KNAPP FÖR ATT HÄMTA FLER (Ligger utanför gissningsformuläret)
    if st.button("Hämta 5 ledtrådar till"):
        with st.spinner("Hämtar fler ledtrådar..."):
            nya_ledtradar = hamta_ledtradar(st.session_state.hemligt_ord)
            st.session_state.ledtradar.extend(nya_ledtradar)
            st.rerun()

    st.divider()

    with st.form("guess", clear_on_submit=True):
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
