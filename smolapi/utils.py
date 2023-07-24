from functools import reduce
import typing


def get_dict_item(
    __d: dict, __key: str, default: typing.Any = None, deep: bool = False
):
    """
    Get dictionary item

    Args:
        __d (dict): Dictionary
        
        __key (typing._KT): Key want to get
        **Note: If you want to get deep item, write key separate level by "."
        
        default (typing.Any, optional): Default value if not found. Defaults to None.
        
        deep (bool, optional): Get item by deep or not. Defaults to False.

    Returns:
        _type_: Value of item by key of dictionary
    """
    if not deep:
        return __d.get(__key, default)
    else:
        return reduce(
            lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
            __key.split("."),
            __d,
        )
