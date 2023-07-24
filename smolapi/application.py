import os
from .types import Scope, Receive, Send, App
from .request import Request
from .routing import Route, Router
from smolapi.setting import LazySetting, settings
import logging

class Application:
    # __app: ASGIApp
    def __init__(self, root_dir: str) -> None:
        if not root_dir:
            raise AttributeError("Set the fucking root directory of project")
        self.__root_dir = root_dir

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> App:
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    # On start up application
                    self.__bootstrap()
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    # On shutdown application
                    await send({"type": "lifespan.shutdown.complete"})
        else:
            routes = Router(
                Router(
                    Route.get("/", None),
                    Route.post("/", None),
                    Route.get("/{id}", None),
                    Route.patch("/{id}", None),
                    Route.delete("/{id}", None),
                    Router(
                        Route.get("/", None),
                        Route.post("/", None),
                        Route.get("/{contact_id}", None),
                        Route.patch("/{contact_id}", None),
                        Route.delete("/{contact_id}", None),
                        prefix="{id}/contact",
                    ),
                    prefix="user",
                ),
            )
            routes.add_route(Route.get("/", None))
            routes.add_route(Route.get("/healthcheck", None))
            for route in routes.unpack_route():
                print(route.__dict__())

    def __bootstrap(self):
        print("Running all essential provider for project")
        globals()["app_root"] = self.__root_dir
        LazySetting.load_setting()
        print(settings.MODULE_A)