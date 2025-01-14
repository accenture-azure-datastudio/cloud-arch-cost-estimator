import base64
import os
from typing import Any, Dict, List

import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from openai_client import AzureOpenAIClient
from prompt import CloudOptimisationPrompt

from menu import menu

class OptimiserApp:
    def __init__(self):
        self.openai_client = AzureOpenAIClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
            deployment=os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
        )

    def run(self):
        st.set_page_config(page_title="Cloud Architecture Optimiser")
        st.title("Cloud Architecture Optimiser")
        menu()
        self.__show_sidebar()
        self.__upload_arch_diagram()

    def __show_sidebar(self):
        st.sidebar.header("Configure your architecture")
        self.provider = st.sidebar.selectbox("Cloud Provider", ("GCP", "AWS", "Azure"))
        self.service_tier = st.sidebar.selectbox(
            "Service Tier", ("Standard", "Developer", "Premium")
        )
        self.price_range = st.sidebar.slider("Price Range (£)", 0, 1000000, 1000, 10)

    def __upload_arch_diagram(self):
        # Uploads image and displays image
        # st.sidebar.header("Upload your architecture")
        uploaded_file = st.file_uploader(
            "Upload your architecture diagram and I will give optimisation recommendations.", type=["png", "jpg"]
        )
        if uploaded_file is not None:
            st.write("You uploaded the image below. Let's optimise this architecture.")
            self.__display_image(uploaded_file=uploaded_file)
            response = self.__identify_services(image=uploaded_file)
            self.__display_response(response)
        else:
            st.warning(
                "Upload an image to get started."
            ) 

    def __display_image(self, uploaded_file: UploadedFile):
        display_image = Image.open(uploaded_file)
        st.image(display_image, use_container_width=True)

    def __identify_services(self, image: UploadedFile):
        base64_img = self.__convert_uploaded_img_to_base64(image=image)

        prompt_generator = CloudOptimisationPrompt(base64_image=base64_img)
        identify_service_prompt = prompt_generator.generate_identify_service_prompt()
        identify_service_response = self.__generate_response(
            messages=identify_service_prompt
        )
        optimisation_prompt = prompt_generator.synthesise_optimisation_prompt(
            previous_response=identify_service_response
        )
        optimisation_response = self.__generate_response(
            messages=optimisation_prompt
        )
        return optimisation_response

    def __generate_response(self, messages: List[Dict[str, Any]]) -> str:
        return self.openai_client.generate_response(messages=messages)

    def __display_response(self, response: str):
        st.subheader("Azure OpenAI Response")
        st.write(response)

    def __convert_uploaded_img_to_base64(self, image: UploadedFile) -> str:
        """
        Convert the uploaded file to a base64 string.
        """
        base64_image = base64.b64encode(image.getvalue()).decode()
        return base64_image


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(".env")

    app = OptimiserApp()
    app.run()


# def landing_page(openai_client):
    # upload_image_sidebar()
    # upload_image_drag_drop()

    # with st.form("my_form"):
    #     text = st.text_area(
    #         "Enter text:",
    #         "What is the cost of the displayed architecture in the image above?",
    #     )
    #     submitted = st.form_submit_button("Submit")
    #     if submitted:
    #         generate_response(openai_client, text)

# def upload_image_sidebar():
#     # Uploads image and displays image
#     st.sidebar.header('Upload your architecture')
#     uploaded_file = st.sidebar.file_uploader("Upload your architecture diagram", type=["png", "jpg"])
#     if uploaded_file is not None:
#         st.write("You uploaded the image below:")
#         display_image = Image.open(uploaded_file)
#         st.image(display_image, use_container_width=True)
#     else:
#        st.write("Let's estimate your architecture. Upload an image in the sidebar.") # can we consider drag and drop interface?

# def upload_image_drag_drop():
#     # Uploads image and displays image
#     drag_drop_file = st.file_uploader("Upload your architecture diagram", type=["png", "jpg"])
#     if drag_drop_file is not None:
#         st.write("You uploaded the image below:")
#         display_image = Image.open(drag_drop_file)
#         st.image(display_image, use_container_width=True)
#     else:
#        st.write("Let's estimate your architecture. Upload an image in the sidebar.") # can we consider drag and drop interface?


