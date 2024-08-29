import openai
import pypdf
import re
import json
import requests
from plugins.ttpschef.app import data

client = openai.OpenAI(api_key='Your API KEY!!')
train_data = data.get_train_data()

class openaiAPI:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        print(text)
        return text



    @staticmethod
    def identify_mitre_attack_techniques(text):

        messages = [
            {"role": "system", "content": "You are an expert in cybersecurity and MITRE ATT&CK framework."},
            {"role": "user", "content": f"""
            Analyze the following text and identify any MITRE ATT&CK techniques used. List the techniques identified and provide a brief explanation (technique_ID, Name, UUID) for each:

            {text}

            Identified MITRE ATT&CK Techniques:
            """},
            {"role": "system", "content":"No limit on the number of techniques"},
            {"role": "system", "content": "Do a technique analysis with only the data and uuid I provided in the messages field. Don't modify uuid at your discretion."}

            ,*train_data
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=messages,
            temperature=0.0,
            n=1,
        )
        message_content = response.choices[0].message.content
        print(f"Full response content: {message_content}")  # 전체 응답 내용 출력

        # UUID 패턴 수정
        #uuid_pattern = r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
        uuid_pattern = r"\b[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}\b|[0-9a-f]{32}\b"

        uuids = re.findall(uuid_pattern, message_content)
        print(f"Extracted UUIDs: {uuids}")
        return uuids

    @staticmethod
    def create_adversary_api(name, description, atomic_ordering):
        url = 'http://localhost:8888/api/v2/adversaries'
        headers = {
            'Content-Type': 'application/json',
            'KEY': 'ADMIN123'
        }

        data = {
            "name": name,
            "description": description,
            "atomic_ordering": atomic_ordering
        }

        try:
            print("Sending request...")
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
            print("success")
            if response.status_code == 200:
                print("Adversary created successfully:", response.json())
                return response.json()
            else:
                print("Failed to create adversary:", response.status_code, response.text)
                return {"status": "error", "message": response.text}
        except requests.exceptions.Timeout:
            print("Request timed out")
            return {"status": "error", "message": "Request timed out"}
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return {"status": "error", "message": str(e)}