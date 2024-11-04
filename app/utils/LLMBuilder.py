from typing import Optional, List, Mapping, Any
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()



headers = {"Authorization": f"Bearer {os.getenv('cloudfareToken')}"}

class OurLLM(CustomLLM):
    system_prompt: Optional[str] = """You are a User Assistant which responds to User Queries using the context provided from the User files\nRespond to user appropriately\n\n if context is not provided use ypur knowledge base to answer and tell them that this is from you and context was empty"""
    context_window: int = 4096
    num_output: int = 512
    modelName: str = "CloudfareLLMLLama3"
    dummy_response: str = "My response"

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.modelName,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        inputs = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{prompt}"}
        ]
        input_data = {"messages": inputs}
        response = requests.post(f"{os.getenv('API_BASE_URL')}@cf/meta/llama-3-8b-instruct", headers=headers, json=input_data)

        return CompletionResponse(text=response.json()["result"]["response"])

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        inputs = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{prompt}"}
        ]
        input_data = {"messages": inputs, "stream": True}
        try:
            resp = requests.post(f"{os.getenv('API_BASE_URL')}@cf/meta/llama-3-8b-instruct", headers=headers, json=input_data, stream=True)

            response = ""
            for chunk in resp.iter_lines(decode_unicode=True):
                if chunk:
                    # Decode the chunk
                    decoded_chunk = chunk

                    if decoded_chunk.startswith("data: "):
                        json_string = decoded_chunk.strip()[6:]
                        try:
                            json_data = json.loads(json_string)
                            response_text = json_data.get("response", "")
                            response += response_text
                            yield CompletionResponse(text=response, delta=response_text)
                        except json.JSONDecodeError:
                            return "there was error on the server side"
        except Exception as e:
            print(e)
            yield e        
                    
llm = OurLLM()                    
