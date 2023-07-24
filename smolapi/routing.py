import typing
import re
from .enums import HttpMethod
import inspect


__all__ = ["Route", "Router"]


_ALLOWED_PATH_PARAMETER_CHARS = "[a-zA-Z0-9\_\-]+"
_PATH_PARAMETER_REGEX = f"""{{({_ALLOWED_PATH_PARAMETER_CHARS})}}"""
_REPLACED_STRING = "(?P<\\1>[a-zA-Z0-9\_\-]+)"


class Route:
    def __init__(
        self: typing.Self,
        url: str,
        function: typing.Callable = None,
        methods: typing.List[HttpMethod] = [],
        middlewares: typing.List = [],
        name: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
    ) -> None:
        self._url = url
        self._function = function
        self._methods = methods
        self._middlewares = middlewares
        self._name = name
        self._description = description

    def __dict__(self):
        return {
            "pattern": self.pattern,
            "url": self._url,
            "method": self._methods,
            "function": self._function,
            "name": self.name,
        }

    @property
    def pattern(self):
        if not hasattr(self, "_pattern") or self._pattern is None:
            regex_str = re.sub("\/+", "/", self._url)  # Remove any extra slash
            regex_str = re.sub(_PATH_PARAMETER_REGEX, _REPLACED_STRING, regex_str)

            self._pattern = f"^/?{regex_str}/?$"
        return self._pattern

    @property
    def url(self) -> str:
        return self._url

    @property
    def methods(self) -> typing.List[HttpMethod]:
        return self._methods

    @property
    def root(self) -> str:
        return self._root or ""

    @root.setter
    def root(self: typing.Self, value: str) -> None:
        self._root = value
        new_url = f"{self._root}/{self._url}"
        self._url = re.sub("\/+", "/", new_url)
        self._pattern = None  # Reset pattern attribute

    @property
    def name(self: typing.Self) -> str:
        if self._name is None:
            name = self._url.split("/")
            if not name:
                self._name = ".".join(self._methods).lower() + ".default"
            else:
                split_names = []
                for name in self._url.split("/"):
                    if name == "":
                        continue
                    if result := re.findall(_PATH_PARAMETER_REGEX, name):
                        split_names.append(f"p_{result[0]}")
                    else:
                        split_names.append(name)
                if not split_names:
                    split_names.append("default")
                self._name = ".".join(
                    list(map(lambda method: method.name, self._methods))
                    + split_names
                ).lower()
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def get_path_parameters_value(self, url: str) -> typing.Dict[str, typing.Any]:
        values: typing.Optional[re.Match[str]] = re.match(self._pattern, url)
        print(self._pattern, self._url)
        if not values:
            raise ValueError("URL not match with pattern")
        return values.groupdict()

    @classmethod
    def get(
        cls, url, function: typing.Callable, name=None, description=None, middlewares=[]
    ) -> typing.Self:
        return Route(
            url=url,
            function=function,
            middlewares=middlewares,
            methods=[HttpMethod.GET, HttpMethod.HEAD],
            name=name,
            description=description,
        )

    @classmethod
    def post(
        cls, url, function: typing.Callable, name=None, description=None, middlewares=[]
    ) -> typing.Self:
        return Route(
            url=url,
            function=function,
            middlewares=middlewares,
            methods=[HttpMethod.POST],
            name=name,
            description=description,
        )

    @classmethod
    def put(
        cls, url, function: typing.Callable, name=None, description=None, middlewares=[]
    ) -> typing.Self:
        return Route(
            url=url,
            function=function,
            middlewares=middlewares,
            methods=[HttpMethod.PUT],
            name=name,
            description=description,
        )

    @classmethod
    def patch(
        cls, url, function: typing.Callable, name=None, description=None, middlewares=[]
    ) -> typing.Self:
        return Route(
            url=url,
            function=function,
            middlewares=middlewares,
            methods=[HttpMethod.PATCH],
            name=name,
            description=description,
        )

    @classmethod
    def delete(
        cls, url, function: typing.Callable, name=None, description=None, middlewares=[]
    ) -> typing.Self:
        return Route(
            url=url,
            function=function,
            middlewares=middlewares,
            methods=[HttpMethod.DELETE],
            name=name,
            description=description,
        )


class Router:
    def __init__(
        self: typing.Self,
        *args,
        prefix: str = "",
        middlewares: typing.List[typing.Callable] = [],
    ) -> None:
        for arg in list(args):
            if not isinstance(arg, Route) and not isinstance(arg, Router):
                raise SyntaxError("Route must be an instance of class Route or Router")
        self._routes = list(args)
        self._prefix = prefix
        self._middlewares = middlewares

    def __dict__(self: typing.Self):
        return dict(self.unpack_route())

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._prefix = value

    @property
    def root(self) -> str:
        return self._root

    @root.setter
    def root(self, value: str) -> None:
        self._root = value

    def add_route(self, route: Route) -> None:
        self._routes.append(route)

    def add_middleware(self, middleware: typing.Callable) -> None:
        self._middlewares.append(middleware)

    def unpack_route(self) -> typing.List[Route]:
        routes = []
        for route in self._routes:
            if isinstance(route, Route) or issubclass(route.__class__, Route):
                route.root = self.prefix
                routes.append(route)
                continue

            if isinstance(route, Router):
                route.prefix = f"{self.prefix}/{route.prefix}"
                sub_routes = route.unpack_route()
                routes += sub_routes

        return routes



