import os
import streamlit as st
from openai import AzureOpenAI
from PIL import Image

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


def landing_page(openai_client):
    st.set_page_config(page_title="Cloud Architecture Cost Estimator")
    st.title("Cost Estimator")
    sidebar_config()
    upload_image()
    # _ = st.sidebar.text_input("Sidebar")

    with st.form("my_form"):
        text = st.text_area(
            "Enter text:",
            "What is the cost of the displayed architecture in the image above?",
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            generate_response(openai_client, text)

def upload_image():
    # Uploads image and displays image
    st.sidebar.header('Upload your architecture')
    # st.sidebar.markdown("[Example CSV input file](link)")
    uploaded_file = st.sidebar.file_uploader("Upload your architecture diagram", type=["png", "jpg"])
    if uploaded_file is not None:
        st.write("You uploaded the image below:")
        display_image = Image.open(uploaded_file)
        st.image(display_image, use_container_width=True)
    else:
       st.write("Let's estimate your architecture. Upload an image in the sidebar.") # can we consider drag and drop interface?

def sidebar_config():
    st.sidebar.header('Configure your architecture')
    provider = st.sidebar.selectbox('Cloud Provider',('GCP','AWS','Azure'))
    service_tier = st.sidebar.selectbox('Service Tier',('Standard','Developer', 'Premium'))
    price_range = st.sidebar.slider('Price Range (£)', 0,1000000, 1000, 10)
    data = {'provider': provider,
            'service_tier': service_tier,
            'price_range': price_range}


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(".env")
    openai_client = create_openai_client()
    landing_page(openai_client=openai_client)
