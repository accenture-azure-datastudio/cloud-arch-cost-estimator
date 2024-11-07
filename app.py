import os

import streamlit as st
from openai import AzureOpenAI


def create_openai_client():
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    )
    return client


def generate_response(client, prompt):
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    response_content = response.choices[0].message.content
    st.info(response_content)


def home_page(openai_client):
    st.set_page_config(page_title="🦜🔗 Quickstart App")
    st.title("🦜🔗 Quickstart App")

    _ = st.sidebar.text_input("Sidebar")
    with st.form("my_form"):
        text = st.text_area(
            "Enter text:",
            "What are the three key pieces of advice for learning how to code?",
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            generate_response(openai_client, text)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(".env")
    openai_client = create_openai_client()
    home_page(openai_client=openai_client)
