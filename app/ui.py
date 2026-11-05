import os

import requests
import streamlit as st

st.set_page_config(page_title="PRGuard", page_icon="🛡️")
st.title("PRGuard")
st.caption("Revisor local de seguridad con IA · LangChain + Qwen + Bandit")
st.write("Repositorio: `demo_repo/` (revisión local y de solo lectura)")

if st.button("Analizar repositorio", type="primary"):
    with st.spinner("Analizando código..."):
        try:
            url = os.getenv("API_URL", "http://127.0.0.1:8000")
            response = requests.post(f"{url}/analyze", timeout=240)
            response.raise_for_status()
            st.session_state["report"] = response.json()["report"]
        except (requests.RequestException, ValueError, KeyError) as exc:
            st.error(f"Error durante el análisis: {exc}")

if "report" in st.session_state:
    st.markdown(st.session_state["report"])
    st.download_button(
        "Descargar informe Markdown",
        st.session_state["report"],
        file_name="prguard-report.md",
        mime="text/markdown",
    )
