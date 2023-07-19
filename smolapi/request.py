from collections.abc import MutableMapping, Mapping
import json
import re
import typing
from .types import Scope, Receive, Send
from urllib.parse import unquote
from functools import reduce
# from core.types import Headers as HeadersType
from http import cookies as http_cookies
# It's stupid but it work, mostly
REGEX_QUERY_STRING=r"^(.*?)=(.*)$"
COOKIE_KEYS = b"cookie"

HeadersType = typing.List[typing.Tuple[bytes, bytes]]

class Query(Mapping[str, typing.Any]):
    def __init__(self, scope: Scope) -> None:
        self.query_string = scope.get("query_string", b"")
        query_arr = str(self).split('&')
        query_dict = {}
        for v in query_arr:
            matches = re.search(REGEX_QUERY_STRING, v, re.IGNORECASE) 
            assert matches, f"Incorrect query string {v}"
            matches = matches.groups()
            key = matches[0]
            value = matches[1]
            if query_dict.get(key, None):
                query_dict.get(key).append(value)
            else:
                query_dict[key] = [value]
        self._query_dict = query_dict
    
    def __str__(self) -> str:
        return unquote(self.query_string.decode("utf-8"))
    
    def __getitem__(self, __key: str) -> typing.Any:
        data = self._query_dict.get(__key)
        return data if len(data) > 1 else data[0]
    
    def __dict__(self) -> dict:
        return self._query_dict
    
    def __iter__(self) -> typing.Iterator:
        return iter(self._query_dict)
    
    def __len__(self) -> int:
        return len(self._query_dict)
    

class Headers(Mapping[str, str]):
    def __init__(self, scope: Scope) -> None:
        headers: HeadersType = scope.get("headers", [])
        headers_dict: dict[str, str] = reduce(lambda prev, item: {**prev, item[0].decode("latin-1"): item[1].decode("latin-1")}, headers, {})
        self._headers = headers
        self._headers_dict = headers_dict
    
    def __getitem__(self, __key: str) -> str:
        return self._headers_dict.get(__key, None)
    
    def __dict__(self) -> dict[str, str]:
        return self._headers_dict
    
    def __iter__(self) -> typing.Iterator:
        return iter(self._headers_dict)
    
    def __len__(self) -> int:
        return len(self._headers_dict)
    
    

class Cookie(Mapping[str,str]):
    def __init__(self, scope: Scope) -> None:
        headers: HeadersType = scope.get("headers", [])
        cookie: typing.Optional[typing.Tuple[bytes, bytes]] = next(filter(lambda item: item[0].lower() == COOKIE_KEYS, headers), None)
        
        if not cookie:
            self._cookie_dict = {}
            return
        self._cookie = http_cookies._unquote(cookie[1].decode("utf-8"))
        cookie_vals: typing.List[str] = self._cookie.split(";")
        cookie_dict: dict[str, str] = {}
        for v in cookie_vals:
            matches = re.search(REGEX_QUERY_STRING, v, re.IGNORECASE)
            assert matches, f"Incorrect format for cookie string {v}"
            matches = matches.groups()
            cookie_dict[matches[0]] = matches[1]
        
        self._cookie_dict = cookie_dict

    def __getitem__(self, __key: str) -> str:
        return self._cookie_dict.get(__key, None)
    
    def __dict__(self) -> dict[str, str]:
        return self._cookie_dict
    
    def __iter__(self) -> typing.Iterator:
        return iter(self._cookie_dict)
    
    def __len__(self) -> int:
        return len(self._cookie_dict)
    
class URI(Mapping[str, str]):
    def __init__(self, scope: Scope) -> None:
        self._scope = scope
    
class Request(Mapping[str, typing.Any]):
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.scope = dict(scope)
        self._receive = receive
        self._send = send
        self._is_stream_finished = False
        self._disconnected = False
    
    def __getitem__(self, __key: str) -> typing.Any:
        return self.scope.get(__key, None)
    
    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.scope)
    
    def __len__(self) -> int:
        return len(self.scope)
    
    @property
    def method(self) -> str:
        return self.scope["method"]
    
    @property
    def scheme(self) -> str:
        return self.scope["scheme"]
    
    @property
    def headers(self) -> Headers:
        if not hasattr(self, "_header"):
            setattr(self, "_header", Headers(scope=self.scope))
        return self._header
    
    @property
    def query(self) -> Query:
        if not hasattr(self, "_query"):
            setattr(self, "_query", Query(scope=self.scope))
        return self._query
    
    @property
    def cookie(self) -> Cookie:
        if not hasattr(self, "_cookie"):
            setattr(self, "_cookie", Cookie(scope=self.scope))
        return self._cookie
    
    #TODO: Implement this shit later 
    @property
    def url(self) -> typing.NoReturn:
        raise NotImplementedError()
    
    #TODO: Consider move body of http request to synchorous instead of asynchronous, since HTTP request is not a stream
    # Refactor this case to applied with HTTP/2
    
    # @abstractmethod
    async def body(self) -> typing.Optional[typing.Union[dict, str]]:
        
        if not hasattr(self, "_body"):
            if self.method in ["GET", "HEAD"]:
                self._body = None
            chunk_data: typing.List[bytes] = []
            async for chunk in self._stream():
                chunk_data.append(chunk)
            content_type = self.headers.get("content-type")
            self._body = _body_parser(content_type, b"".join(chunk_data)) or None
            
        return self._body

    
    async def _stream(self) -> typing.AsyncGenerator[bytes, None]:
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return
        if self._is_stream_finished:
            return
        self._is_stream_finished = True
        while True:
            data = await self._receive()
            print(data)
            if data["type"] == "http.request":
                body = data["body"] or b""
                if body:
                    yield body
                if not data.get("more_body", False):
                    #End of body
                    break
            elif data["type"] == "http.disconnect":
                self._disconnected = True
                break
            else:
                break
            
        yield b""


def _body_parser(content_type: str, body: bytes) -> typing.Optional[typing.Union[str, dict]]:
    """
    Non stream body parser for http request

    Args:
        content_type (str): request content type
        body (bytes): byte data

    Raises:
        NotImplementedError: Too lazy to implement

    Returns:
        dict: Dict or string of data extracted from body
    """
    content_type_lower = content_type.lower()
    if content_type_lower == "text/plain":
        return body.decode("utf-8")
    if content_type_lower == "application/json":
        return json.loads(body)
    if content_type == "text/xml" or "application/xml":
        raise NotImplementedError()
    
    return None