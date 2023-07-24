from collections.abc import MutableMapping, Mapping
import typing
import importlib
import inspect
from smolapi.utils import get_dict_item
from smolapi.core_object import SingletonInstance


__all__ = ["LazySetting"]

_SETTING_KEY = "app_setting"


#TODO: Improve to avoid using globals object, since globals is shit, mostly...
class GlobalSetting(object):
    """
    Global setting mapping using globals instance
    All the settings will be map with global object, with specific key mentioned
    
    Args:
        object (_type_): _description_

    Returns:
        _type_: _description_
    """

    __metaclass__ = SingletonInstance

    def __init__(self) -> None:
        
        if not globals().get(_SETTING_KEY):
            globals()[_SETTING_KEY] = {}

    def __getattribute__(self, __key: str) -> typing.Any:
        return get_dict_item(globals(), f"{_SETTING_KEY}.{__key}", deep=True)

    def __setattr__(self, __name: str, __value: typing.Any) -> None:
        globals()[_SETTING_KEY][__name] = __value

    def __dict__() -> dict:
        return globals()[_SETTING_KEY]


class LazySetting(object):
    """Somewhat idiotic way of config global setting
    
    Raises:
        LookupError: Failed to find settings.py module in project
    """

    __root = globals().get("app_root")

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def load_setting(cls):
        # print(cls.__root)
        setting_module = inspect.getmodulename(f"{cls.__root}/settings.py")
        if not setting_module:
            raise LookupError(
                f"Can't find settings file, make sure to include settings.py in your project"
            )
        
        module = importlib.import_module(setting_module)
        g = GlobalSetting()
        
        import re
        for k, v in module.__dict__.items():
            if re.match(r"^[A-Z]+(?:_[A-Z]+)*$", k):
                setattr(g, k, v)


settings = GlobalSetting()
