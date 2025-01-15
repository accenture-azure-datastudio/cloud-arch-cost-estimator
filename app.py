import base64
import os
from typing import Any, Dict, List

import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

from menu import menu
from openai_client import AzureOpenAIClient
from prompt import CostEstimationPrompt


class CostEstimatorApp:
    def __init__(self):
        self.openai_client = AzureOpenAIClient(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
            deployment=os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
        )

    def run(self):
        st.set_page_config(page_title="Cloud Architecture Cost Estimator")
        st.title("Cost Estimator")
        menu()
        self.__show_sidebar()

        # initialise chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        uploaded_file_status = self.__upload_arch_diagram()
        if uploaded_file_status:
            self.__show_chat()

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
            "Upload your architecture diagram and I will estimate the implementation cost.",
            type=["png", "jpg"],
        )
        uploaded_file_status = uploaded_file is not None
        if uploaded_file_status:
            st.write(
                "You uploaded the image below. Let's estimate the cost of this architecture."
            )
            self.__display_image(uploaded_file=uploaded_file)
            self.__estimate_cost(image=uploaded_file)
        else:
            st.warning(
                "Upload an image to get started."
            )  # can we consider drag and drop interface? => implemented in the menu.py
        return uploaded_file_status

    def __show_chat(self):
        if prompt := st.chat_input("Provide your feedback"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                stream = self.openai_client.generate_response(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    def __display_image(self, uploaded_file: UploadedFile):
        display_image = Image.open(uploaded_file)
        st.image(display_image, use_container_width=True)

    def __estimate_cost(self, image: UploadedFile):
        base64_img = self.__convert_uploaded_img_to_base64(image=image)

        prompt_generator = CostEstimationPrompt(base64_image=base64_img)
        identify_service_prompt, identify_service_response_format = (
            prompt_generator.generate_identify_service_prompt()
        )
        identify_service_response = self.__generate_response(
            messages=identify_service_prompt,
            response_format=identify_service_response_format,
        )
        cost_estimation_prompt, cost_estimation_response_format = (
            prompt_generator.generate_cost_estimation_prompt(
                previous_response=identify_service_response
            )
        )
        cost_estimation_response = self.__generate_response(
            messages=cost_estimation_prompt,
            response_format=cost_estimation_response_format,
        )

        st.session_state.messages = st.session_state.messages + cost_estimation_prompt
        st.session_state.messages.append(
            {"role": "assistant", "content": cost_estimation_response}
        )
        with st.chat_message("assistant"):
            st.markdown(cost_estimation_response)

    def __generate_response(
        self, messages: List[Dict[str, Any]], response_format=None
    ) -> str:
        return self.openai_client.generate_response(
            messages=messages, response_format=response_format
        )

    def __convert_uploaded_img_to_base64(self, image: UploadedFile) -> str:
        """
        Convert the uploaded file to a base64 string.
        """
        base64_image = base64.b64encode(image.getvalue()).decode()
        return base64_image


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(".env")

    app = CostEstimatorApp()
    app.run()
