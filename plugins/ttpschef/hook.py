from aiohttp import web
from aiohttp_jinja2 import template

from app.service.auth_svc import check_authorization
from plugins.ttpschef.app.openai import openaiAPI
import os
import tempfile

name = 'TTPsChef'
description = 'A sample plugin for demonstration purposes'
address = '/plugin/ttpschef/gui'

async def enable(services):
    app = services.get('app_svc').application
    fetcher = AbilityFetcher(services)
    app.router.add_route('*', '/plugin/ttpschef/gui', fetcher.splash)
    app.router.add_route('POST', '/plugin/ttpschef/upload_and_create', fetcher.upload_and_create)
    app.router.add_route('GET', '/get/ttpschef', fetcher.get_abilities)
    

class AbilityFetcher:
    def __init__(self, services):
        self.services = services
        self.auth_svc = services.get('auth_svc')

    async def get_abilities(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        print(abilities)
        return web.json_response(dict(abilities=[a.display for a in abilities]))

    @check_authorization
    @template('ttpschef.html')
    async def splash(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        return dict(abilities=[a.display for a in abilities])

    async def upload_and_create(self, request):
        reader = await request.multipart()
        field = await reader.next()
        if field.name == 'pdf_file':
            filename = field.filename
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file_path = temp_file.name
            with open(temp_file_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()  # 8192 bytes by default.
                    if not chunk:
                        break
                    f.write(chunk)

            # PDF 텍스트 추출 및 adversary 생성
            text = openaiAPI.extract_text_from_pdf(temp_file_path)
            os.remove(temp_file_path)
            print("1")
            uuids = openaiAPI.identify_mitre_attack_techniques(text)
            # create_result = openaiAPI.create_adversary_api("Adversary from PDF", "Automatically generated", uuids)
            create_result = openaiAPI.create_adversary_api(filename, "Automatically generated", uuids)
            if create_result.get("status") == "error":
                return web.json_response({"status": "error", "message": create_result["message"]})
            return web.json_response({"status": "success", "message": "Adversary created successfully!"})
        return web.json_response({"status": "error", "message": "Invalid request"})