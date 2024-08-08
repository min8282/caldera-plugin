# from app.utility.base_world import BaseWorld
# from plugins.abilities.app.abilities_gui import AbilitiesGUI
# from plugins.abilities.app.abilities_api import AbilitiesAPI

# name = 'Abilities'
# description = 'tteesstt'
# address = '/plugin/abilities/gui'
# access = BaseWorld.Access.RED


# async def enable(services):
#     app = services.get('app_svc').application
#     abilities_gui = AbilitiesGUI(services, name=name, description=description)
#     app.router.add_static('/abilities', 'plugins/abilities/static/', append_version=True)
#     app.router.add_route('GET', '/plugin/abilities/gui', abilities_gui.splash)

#     abilities_api = AbilitiesAPI(services)
#     # Add API routes here
#     app.router.add_route('POST', '/plugin/abilities/mirror', abilities_api.mirror)

from aiohttp_jinja2 import template, web

from app.service.auth_svc import check_authorization

name = 'Abilities'
description = 'A sample plugin for demonstration purposes'
address = '/plugin/abilities/gui'


async def enable(services):
    app = services.get('app_svc').application
    fetcher = AbilityFetcher(services)
    app.router.add_route('*', '/plugin/abilities/gui', fetcher.splash)
    app.router.add_route('GET', '/get/abilities', fetcher.get_abilities)


class AbilityFetcher:
    def __init__(self, services):
        self.services = services
        self.auth_svc = services.get('auth_svc')

    async def get_abilities(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        return web.json_response(dict(abilities=[a.display for a in abilities]))

    @check_authorization
    @template('abilities.html')
    async def splash(self, request):
        abilities = await self.services.get('data_svc').locate('abilities')
        return(dict(abilities=[a.display for a in abilities]))
