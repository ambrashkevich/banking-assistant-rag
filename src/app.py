import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Банковский FAQ-Ассистент", page_icon="🏦")
st.title("🏦 FAQ-Ассистент по банковским продуктам")
st.caption("Курсовая работа по дисциплине ПИС")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Здравствуйте! Чем могу помочь по тарифам и продуктам банка?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Введите ваш вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        response = requests.post(f"{API_URL}/api/v1/chat", json={"question": prompt}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])

            with st.chat_message("assistant"):
                st.write(answer)
                if sources:
                    with st.expander("📚 Источники ответа"):
                        for src in sources:
                            st.write(f"- {src}")

            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Ошибка сервиса API")
    except Exception as e:
        st.error(f"Не удалось подключиться к серверу API: {e}")