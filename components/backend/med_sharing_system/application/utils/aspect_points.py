from typing import List, Callable, Any, TypeAlias
from functools import wraps

Decorator: TypeAlias = Callable[..., Callable[..., Any]]
AnyFunction: TypeAlias = Callable[..., Any]


class DecoratedFunction:
    """
    Представляет собой обертку для функций, предназначенных для декорирования.
    """
    def __init__(self, function: AnyFunction):
        self.function = function

    def decorate(self, *decorators: Decorator):
        """
        Применяет несколько декораторов к функции.
        """
        for decorator in decorators:
            self.function = decorator(self.function)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @classmethod
    def wrap(cls, function: AnyFunction) -> 'DecoratedFunction':
        """
        Создает экземпляр `DecoratedFunction` для заданной функции.
        Устанавливает для этого экземпляра свои поля и методы.
        """
        decorated_function = cls(function)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return decorated_function(*args, **kwargs)

        setattr(wrapper, 'function', function)
        setattr(wrapper, 'decorated_function', decorated_function)
        setattr(wrapper, 'decorate', decorated_function.decorate)

        return wrapper


class DecoratedFunctionRegistry:
    """
    Представляет реестр декорированных функций и предоставляет методы для их управления.
    Этот класс может использоваться для централизованного управления декораторами,
    применяемыми к нескольким функциям. Он позволяет регистрировать новые функции и
    применять декораторы ко всем зарегистрированным функциям или к определенному
    подмножеству.
    """
    def __init__(self):
        self._registry: List[DecoratedFunction] = []

    def apply_decorators(self,
                         *decorators: Decorator,
                         exclude: List[DecoratedFunction] = None
                         ) -> None:
        """
        Применяет декораторы ко всем зарегистрированным функциям.
        """
        exclude = exclude or []
        for decorated_function in self._registry:
            if decorated_function not in exclude:
                decorated_function.decorate(*decorators)

    def register_function(self, function: AnyFunction) -> DecoratedFunction:
        """
        Регистрирует новую функцию и возвращает
        соответствующий ей экземпляр `DecoratedFunction`.
        """
        decorated_function = DecoratedFunction.wrap(function)
        self._registry.append(decorated_function)
        return decorated_function
