import typing

Scope = typing.MutableMapping[str, typing.Any]
Message = typing.MutableMapping[str, typing.Any]

Send = typing.Callable[[], typing.Awaitable[typing.Any]]

Receive = typing.Callable[[], typing.Awaitable[Message]]

App = typing.Callable[[Scope, Message, Send], typing.Awaitable[None]]


Headers = typing.List[typing.Tuple[bytes, bytes]]