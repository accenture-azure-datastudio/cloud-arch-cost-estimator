from typing import Any, Dict, List

from openai import AzureOpenAI


class AzureOpenAIClient:
    def __init__(
        self, api_key: str, api_version: str, azure_endpoint: str, deployment: str
    ) -> None:
        """
        Initialize the AzureOpenAIClient with the given parameters.
        """
        self.api_key = api_key
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint
        self.deployment = deployment
        self.client = self._create_azure_openai_client()

    def _create_azure_openai_client(self) -> AzureOpenAI:
        """
        Create and return an AzureOpenAI client.
        """
        try:
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint,
            )
            return client
        except Exception as e:
            raise RuntimeError(f"Failed to create AzureOpenAI client: {e}")

    def generate_response(
        self, messages: List[Dict[str, Any]], response_format=None
    ) -> str:
        """
        Generate a response from the Azure OpenAI model based on the given prompt.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                response_format=response_format,
            )
            response_content = response.choices[0].message.content
            return response_content
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {e}")
