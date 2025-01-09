import base64
import json
import os
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit.runtime.uploaded_file_manager import UploadedFile

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
        st.sidebar.header("Upload your architecture")
        uploaded_file = st.sidebar.file_uploader(
            "Upload your architecture diagram", type=["png", "jpg"]
        )
        if uploaded_file is not None:
            st.write("You uploaded the image below:")
            self.__display_image(uploaded_file=uploaded_file)
            response_list = self.__estimate_cost(image=uploaded_file)
            self.__display_response(response_list)
        else:
            st.write(
                "Let's estimate your architecture. Upload an image in the sidebar."
            )  # can we consider drag and drop interface?

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
        cost_estimation_df, total_estimated_cost = (
            self.__format_cost_estimation_response(cost_estimation_response)
        )
        return [cost_estimation_df, total_estimated_cost]

    def __format_cost_estimation_response(self, json_str) -> pd.DataFrame:
        json_dict = json.loads(json_str)
        services_dict = json_dict["services"]
        total_estimated_cost = json_dict["total_estimated_monthly_cost"]
        df = pd.DataFrame.from_records(services_dict)
        return df, total_estimated_cost

    def __generate_response(
        self, messages: List[Dict[str, Any]], response_format=None
    ) -> str:
        return self.openai_client.generate_response(
            messages=messages, response_format=response_format
        )

    def __display_response(self, response_list: List[Any]):
        st.subheader("Estimated Cost")
        for response in response_list:
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

    app = CostEstimatorApp()
    app.run()
