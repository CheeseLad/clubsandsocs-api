from typing import Any, TypeGuard, TypeVar

T_ = TypeVar("T_")


def is_obj_list(val: list[Any], obj: type[T_]) -> TypeGuard[list[T_]]:
    return all(isinstance(x, obj) for x in val)
