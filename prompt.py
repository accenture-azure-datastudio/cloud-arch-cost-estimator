from typing import Any, Dict, List, Tuple

from pydantic import BaseModel


class CostEstimate(BaseModel):
    services: str
    assumptions: list[str]
    price_rate: str
    monthly_cost_estimate: str


class CostEstimationPrompt:
    def __init__(self, base64_image: str) -> None:
        self.base64_image = base64_image
        self.system_prompt = self.__generate_system_prompt()

    def __generate_system_prompt(self) -> Dict[str, Any]:
        system_prompt = {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a solution architect. Your goal is to analyze architecture diagrams and estimate the cost of cloud services. Assume that all resources are created in UK and currency is in British Pound. Your tasks include: \n1. Identifying the cloud services used in the diagram.\n2. Determining the quantity of each service if specified. \n3. Make any sensible assumptions for each services such as compute options, data volume, token estimation, models etc. \n4. Based on the latest pricing information from cloud service providers, provide a cost estimation based on the identified services and quantities, include any assumptions made for each services.",
                }
            ],
        }
        return system_prompt

    def generate_identify_service_prompt(self) -> Tuple[List[Dict[str, Any]], None]:
        identify_service_prompt = [
            self.system_prompt,
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                                    Identify the cloud services used in the diagram and determine the quantity of each service if specified.
                                """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self.base64_image}"
                        },
                    },
                ],
            },
        ]
        self.identify_service_prompt = identify_service_prompt
        response_format = None
        return self.identify_service_prompt, response_format

    def generate_cost_estimation_prompt(
        self, previous_response: str
    ) -> Tuple[List[Dict[str, Any]], CostEstimate]:
        assistant_response = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": f"{previous_response}",
                },
            ],
        }

        cost_estimation_prompt = (
            self.identify_service_prompt
            + [assistant_response]
            + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Based on the cloud services identified, use latest pricing information from cloud service providers, provide a monthly cost estimation based on the identified services and quantities, include any assumptions made for each services. For each service, format the output as '**Assumptions** \n**Pricing Rate**\n**3. Monthly Cost**.' Aggregate the total monthly cost for each services in the end.",
                        }
                    ],
                },
            ]
        )
        self.cost_estimation_prompt = cost_estimation_prompt
        response_format = {"type": "json_object"}
        return self.cost_estimation_prompt, response_format


class CloudOptimisationPrompt:
    def __init__(self, base64_image: str) -> None:
        self.base64_image = base64_image
        self.system_prompt = self.__generate_system_prompt()

    def __generate_system_prompt(self) -> Dict[str, Any]:
        system_prompt = {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": """You are a solution architect. Your goal is to analyze architecture diagrams and consider substitutes of listed cloud resources. Assume that all resources are created in UK and currency is in British Pound. Your tasks include: 
                    1. Identifying the cloud services used in the diagram.
                    2. Determining the quantity of each service if specified. 
                    3. Based on the latest pricing information from cloud service providers, provide a cost estimation based on the identified services and quantities, include any assumptions made for each services.
                    4. Make any sensible assumptions for each services such as compute options, data volume, token estimation, models etc. 
                    5. Identify the potential substitutes for the identified services and provide a cost estimation based on the substitutes.""",
                }
            ],
        }
        return system_prompt

    def generate_identify_service_prompt(self) -> List[Dict[str, Any]]:
        identify_service_prompt = [
            self.system_prompt,
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
                                    Identify the cloud services used in the diagram and determine the quantity of each service if specified.
                                """,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self.base64_image}"
                        },
                    },
                ],
            },
        ]
        self.identify_service_prompt = identify_service_prompt
        return self.identify_service_prompt

    def synthesise_optimisation_prompt(
        self, previous_response: str
    ) -> List[Dict[str, Any]]:
        assistant_response = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": f"{previous_response}",
                },
            ],
        }

        optimisation_prompt = (
            self.identify_service_prompt
            + [assistant_response]
            + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Based on the cloud services identified, use latest pricing information from alternate cloud service providers, provide a monthly cost estimation based on the alternatives of identified services from other cloud providers. Include any assumptions made for each services. For each service, format the output as '**Assumptions** \n**Pricing Rate**\n**3. Monthly Cost**.' Aggregate the total monthly cost for the cheapest alternative services in the end.",
                        }
                    ],
                },
            ]
        )
        self.optimisation_prompt = optimisation_prompt
        return self.optimisation_prompt
