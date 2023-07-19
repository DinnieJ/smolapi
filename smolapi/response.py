import typing 
from .types import Scope, Receive, Send
from abc import ABC, abstractproperty

class HttpResponse(ABC):
    
    
    def __init__(self) -> None:
        pass
    
    @property
    @abstractproperty
    def content_type(self):
        return "text/plain"
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> Any:
        await send({
            
        })

class JsonResponse(HttpResponse):
    
    def __init__(self) -> None:
        super().__init__()
        
    @property
    def content_type(self):
        return "application/json"
    