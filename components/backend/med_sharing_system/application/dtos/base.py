from typing import Union, get_args, get_origin, TypeAlias

from pydantic import BaseModel as BaseSchema
from med_sharing_system.application import entities

class_: TypeAlias = type(entities.Entity)


class DTO(BaseSchema):
    def populate_obj(self, obj, **kwargs) -> entities.Entity:
        """
        Заполняет или обновляет объект данными из DTO.
        В том числе и вложенные объекты.

        :param self: Экземпляр DTO.
        :param obj: Экземпляр класса.

        :return: Обновленный объект.
        """
        self._set_exclude_unset(kwargs)

        dto_data: dict = self.dict(**kwargs)
        obj_data: dict = self._populate_nested_obj_if_exists(obj, dto_data)

        return self._populate_obj(obj, obj_data)

    def create_obj(self, cls, **kwargs) -> entities.Entity:
        """
        Создает и заполняет объект данными из DTO.
        В том числе и вложенные объекты.

        :param self: Экземпляр DTO.
        :param cls: Класс.

        :return: Созданный объект.
        """
        self._set_exclude_unset(kwargs)

        dto_data: dict = self.dict(**kwargs)
        cls_data: dict = self._create_nested_objs_if_exists(dto_data, cls)

        return cls(**cls_data)

    @staticmethod
    def _set_exclude_unset(kwargs):
        if 'exclude_unset' not in kwargs:
            kwargs['exclude_unset'] = True

    def _create_nested_objs_if_exists(self, dto_data: dict, outer_cls: class_) -> dict:
        """
        Создает вложенные объекты `outer_cls`, и заполняет их данными из DTO.

        :param dto_data: Данные DTO для создания вложенных объектов.
        :param outer_cls: Внешний класс, который хранит вложенные классы.

        :return: Обновленные данные DTO после создания вложенных объектов.
        """
        nested_classes: dict[str, class_] = self._get_nested_classes(self, outer_cls)

        if nested_classes:
            for field_name, nested_cls in nested_classes.items():
                nested_data: dict = dto_data[field_name]
                new_nested_instance: entities.Entity = nested_cls(**nested_data)
                dto_data[field_name] = new_nested_instance

        return dto_data

    def _populate_nested_obj_if_exists(self, outer_obj: entities.Entity, dto_data: dict) -> dict:
        """
        При существовании вложенных объектов(экземпляров классов) в `outer_obj`, заполняет их данными из DTO.

        :param outer_obj: Внешний объект, который хранит вложенные объекты(экземпляры классов).
        :param dto_data: Данные DTO для заполнения вложенных объектов.

        :return: Обновленные данные DTO после заполнения/обновления вложенных объектов.
        """
        nested_classes: dict[str, entities.Entity] = self._get_nested_classes(self, outer_obj)

        if nested_classes:
            for field_name in nested_classes.keys():
                nested_obj: entities.Entity = getattr(outer_obj, field_name)
                nested_obj_data: dict = dto_data[field_name]
                dto_data[field_name] = self._populate_obj(nested_obj, nested_obj_data)

        return dto_data

    @staticmethod
    def _get_nested_classes(dto: BaseSchema, outer_cls: entities.Entity) -> dict[str, class_] | dict[None]:
        """
        Пример:
        {
            'category': <class 'application.entities.ItemCategory'>,
            'type': <class 'application.entities.ItemType'>
        }
        """
        only_nested_dto_fields: list = [key for key, value in dto if isinstance(value, BaseSchema)]

        nested_classes: dict[str, class_] = {}
        for field in only_nested_dto_fields:
            class_name = outer_cls.__annotations__.get(field)
            if get_origin(class_name) is Union:
                class_name = get_args(class_name)[0]
            nested_classes[field] = class_name

        return nested_classes

    @staticmethod
    def _populate_obj(obj, obj_data: dict) -> entities.Entity:
        for key, value in obj_data.items():
            setattr(obj, key, value)
        return obj
