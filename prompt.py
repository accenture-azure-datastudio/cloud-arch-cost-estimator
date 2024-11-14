from typing import Any, Dict, List


def generate_identify_service_messages(base64_image: str) -> List[Dict[str, Any]]:
    identify_service_prompt = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a solution architect. Your goal is to identify the cloud services in the image provided.",
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What are the cloud services described in this image? Include the quantity if available.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ]
    return identify_service_prompt
