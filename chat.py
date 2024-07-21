from openai import OpenAI
import anthropic
import json

class chat:
    system_message = "You can answer questions based on a piece of source material. Given a question and text from an official source you answer the question using the source information in a clear, concise and accurate way. Use paragraph form for you answer"

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.client = None

        if llm_provider == "anthropic":
            self.client = anthropic.Anthropic()
        elif llm_provider == "openai":
            client = OpenAI()
        else:
            raise ValueError()

    def create_response(self, query, source_title):
        response = None

        f = open(source_title, "r")
        text = f.read()

        if self.llm_provider == "anthropic":
            message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=300,
            temperature=0.3,
            system=chat.system_message,
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"question: {query}, source: {text}"
                            }
                        ]
                    }
                ]
            )
            response = message.content[0].text

        elif self.llm_provider == "openai":
            res = self.client.chat.completions.create(
              model="gpt-4o-mini",
              response_format={ "type": "json_object" },
              messages=[
                {"role": "system", "content": chat.system_message},
                {"role": "user", "content":f"question: {query}, source: {text}"}
              ]
            )
            response = res.choices[0].message.content
        
        return response