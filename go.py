import streamlit as st
from openai import OpenAI
import re

# Kontrollera API-nyckel
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("Nyckeln saknas i Streamlit Cloud Secrets!")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

st.set_page_config(page_title="Gissa Ordet", page_icon="🎮")
st.title("🎮 Gissa Ordet: AI-utmaningen")

# Initiera spelet
if "hemligt_ord" not in st.session_state: st.session_state.hemligt_ord = ""
if "ledtradar" not in st.session_state: st.session_state.ledtradar = []

# --- STEG 1: STARTA ---
if not st.session_state.hemligt_ord:
    with st.form("setup"):
        valt_ord = st.text_input("Välj ett hemligt ord:")
        if st.form_submit_button("Starta spelet") and valt_ord:
            st.session_state.hemligt_ord = valt_ord.strip().lower()
            with st.spinner("AI:n skapar ledtrådar..."):
                try:
                    res = client.chat.completions.create(
                        model="meta-llama/llama-3.2-3b-instruct:free",
                        messages=[
                            {"role": "system", "content": "Skriv 5 korta ledtrådar på svenska som börjar med 'Som...' eller 'Liknar...'. En per rad."},
                            {"role": "user", "content": f"Ordet är: {st.session_state.hemligt_ord}"}
                        ]
                    )
                    st.session_state.ledtradar = [r.strip() for r in res.choices[0].message.content.split('\n') if len(r.strip()) > 3]
                    st.rerun()
                except Exception as e:
                    st.error(f"Kunde inte hämta ledtrådar: {e}")
                    st.session_state.hemligt_ord = ""

# --- STEG 2: SPELA ---
else:
    st.success(f"✅ Ordet är dolt! Det finns {len(st.session_state.ledtradar)} ledtrådar.")
    
    for i, ledtrad in enumerate(st.session_state.ledtradar, 1):
        st.info(f"Ledtråd {i}: {ledtrad}")

    if st.button("Hämta 5 ledtrådar till"):
        with st.spinner("Hämtar fler..."):
            try:
                res = client.chat.completions.create(
                    model="meta-llama/llama-3.1-8b-instruct:free",
                    messages=[{"role": "user", "content": f"Ge 5 nya ledtrådar för {st.session_state.hemligt_ord} på svenska."}]
                )
                nya = [r.strip() for r in res.choices[0].message.content.split('\n') if len(r.strip()) > 3]
                st.session_state.ledtradar.extend(nya)
                st.rerun()
            except Exception as e:
                st.error(f"Kunde inte hämta fler: {e}")

    st.divider()

    with st.form("guess_form", clear_on_submit=True):
        gissning = st.text_input("Gissa ordet:")
        if st.form_submit_button("Gissa!"):
            # Enkel kontroll om gissningen innehåller ordet
            if st.session_state.hemligt_ord in gissning.lower():
                st.balloons()
                st.success(f"🎉 RÄTT! Ordet var: {st.session_state.hemligt_ord.upper()}")
                if st.button("Spela igen"):
                    st.session_state.clear()
                    st.rerun()
            else:
                st.error("Fel gissat, försök igen!")

if st.sidebar.button("Börja om helt"):
    st.session_state.clear()
    st.rerun()
