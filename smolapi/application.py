
from .types import Scope, Receive, Send, App
from .request import Request

class Application():
    # __app: ASGIApp
    def __init__(self) -> None:
        self._add_healthcheck_router()
        print(self.__app.routes)
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send ) -> App:
        request = Request(scope, receive, send)
        print(scope)
        print(dict(request.headers))
        body = await request.body()
        # body = await request.body()
        # print(body.decode("utf-8"))
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json")
                ],
            }
        )
        await send({"type": "http.response.body", "body": b"{\"Hello\": \"World\"}"})
    
