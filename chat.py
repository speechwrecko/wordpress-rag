from openai import OpenAI
import anthropic
import json

class chat:
    system_message = "You can answer questions based on provided source material. Given a question and text from one or more official sources you answer the question using the source information in a readable, clear, concise and accurate way. Answer the question in paragraph form."

    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
        self.client = None

        if llm_provider == "anthropic":
            self.client = anthropic.Anthropic()
        elif llm_provider == "openai":
            client = OpenAI()
        else:
            raise ValueError()

    def create_response(self, query, path, source_titles):
        response = None

        sources_text = ""
        for index, source_title in enumerate(source_titles):
            f = open(path + "/" + source_title, "r")
            text = f.read()
            sources_text = sources_text + f"source #{index}: {text}\n\n"

        if self.llm_provider == "anthropic":
            message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            temperature=0.3,
            system=chat.system_message,
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"question: {query}, source: {sources_text}"
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