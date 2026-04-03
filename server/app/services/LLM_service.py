from openai import OpenAI

from app.core.prompt import TablePrompts, ImagePrompts, FormulaPrompts


class LLMService:
    """Dùng LLM để mô tả Table, Image, Formula thành text"""

    def __init__(self, client: OpenAI, model: str = "gpt-5-mini"):
        self.client = client
        self.model = model

    def _call(self, input_data) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=input_data,
            )

            return response.output[1].content[0].text.strip()

        except Exception as e:
            print(f"LLM failed: {e}")
            return ""


    def describe_table(self, raw_html: str, context: str = "") -> str:
        return self._call([
            {
                "role": "system",
                "content": TablePrompts.SYSTEM,
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": TablePrompts.INSTRUCTION},
                    {"type": "input_text", "text": f"Context:\n{context or 'None'}"},
                    {"type": "input_text", "text": f"Table HTML:\n{raw_html}"},
                ]
            }
        ])


    def describe_image(self, image_b64: str, context: str = "") -> str:
        return self._call([
            {
                "role": "system",
                "content": ImagePrompts.SYSTEM,
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": ImagePrompts.INSTRUCTION},
                    {"type": "input_text", "text": f"Context:\n{context or 'None'}"},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_b64}"
                    },
                ]
            }
        ])


    def describe_formula(self, formula_text: str, context: str = "") -> str:
        return self._call([
            {
                "role": "system",
                "content": FormulaPrompts.SYSTEM,
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": FormulaPrompts.INSTRUCTION},
                    {"type": "input_text", "text": f"Context:\n{context or 'None'}"},
                    {"type": "input_text", "text": f"Formula:\n{formula_text}"},
                ]
            }
        ])