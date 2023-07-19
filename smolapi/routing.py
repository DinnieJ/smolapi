import typing
import re
from .enums import HttpMethods


_ALLOWED_PATH_PARAMETER_CHARS = '[a-zA-Z0-9\_\-]+'
_PATH_PARAMETER_REGEX = f"""{{({_ALLOWED_PATH_PARAMETER_CHARS})}}"""
_REPLACED_STRING = "(?P<\\1>[a-zA-Z0-9\_\-]+)"


class Route:
    def __init__(
        self: typing.Self,
        url: str,
        function: typing.Callable = None,
        methods: typing.List[HttpMethods] = [],
        middlewares: typing.List = None,
    ) -> None:
        self._url = url
        self._function = function
        self.methods = methods
        self.middlewares = middlewares
    
    @property
    def pattern(self):
        if not hasattr(self, "_pattern"):
            regex_str = self._url
            regex_str = re.sub(_PATH_PARAMETER_REGEX, _REPLACED_STRING, regex_str)
            self._pattern = regex_str
        return self._pattern
    
    
    @property
    def root(self) -> str:
        return self._root or ""

    @root.setter
    def root(self: typing.Self, value: str) -> None:
        self._root = value

    def get_path_parameter(self, url_str: str) -> typing.Dict[str, typing.Any]:
        values = re.match(self._pattern, url_str)
        if not values:
            raise ValueError("URL not match with pattern")
        return values.groupdict()
    
    def set_root_url(self, root: str):
        self._url = f"{root}{self._url}"
        

class Router:
    def __init__(
        self: typing.Self, 
        routes: typing.List[typing.Union[Route, typing.Self]], 
        prefix: str = "", 
        root: typing.Optional[str] = None
    ) -> None:
        self._routes = routes
        self._prefix = prefix
        self._root = root
        
    
    def unpack_route(self) -> typing.List[Route]:
        routes = []
        for route in self._routes:
            if isinstance(route, Route) or issubclass(route.__class__, Route):
                route.root = self._root
                routes.append(route)
                continue
            
            if isinstance(route, Router):
                sub_routes = route.unpack_route()
                routes += sub_routes
        
        return routes
    
        



        
