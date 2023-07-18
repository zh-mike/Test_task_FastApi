from db_api import provider as db

class Model:
    __slots__ = ("_properties", "_modified", "_table_name")
    _fields = {}

    def __init__(self):
        self._properties = self._fields
        self._modified = False

    def __getattr__(self, item):
        if item not in self._properties:
            raise AttributeError(f"Property {item} not initialized")

        return self._properties.get(item)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
            return

        if key not in self._properties:
            raise AttributeError(f"Property {key} not initialized")


        self._properties[key] = value
        self._modified = True

    def get_modified_properties(self) -> dict:
        result = {}

        for k in self._modified_properties:
            result[k] = {"from": self._modified_properties[k][0], "to": self._modified_properties[k][1]}

        return result

    def keys(self):
        return list(self._properties.keys())

    def __getitem__(self, key):
        return self._properties[key]

    def save(self):
        """
        Сохранение изменений в БД
        """
        if self._modified is False:
            return

        params = dict(self._properties)
        del params['id']

        sql = db.insert_str(self._table_name, params)
        result = db.execute(sql, tuple(params.values()), commit=True, lastrowid=True)
        self._properties['id'] = result


    def fill(self, data: dict):
        """
        Наполнение модели данными
        """
        for parameter in self._properties:
            self._properties[parameter] = data.get(parameter, None)


    def update(self):
        """
        Обновление БД
        """

        if self._modified is False:
            return

        params = dict(self._properties)

        sql = db.update_str(self._table_name, params, where={'id': self.id})
        data = db.execute(sql, parameters=tuple(params.values())+(self.id,), commit=True)


    @classmethod
    def delete(cls, id):
        """
        Удаление записи из БД
        """
        sql = db.delete_str(cls._table_name, where={'id': id})
        result = db.execute(sql, (id,), commit=True)


    @classmethod
    def load(cls, conditions: dict = {}):
        """
        Загрузка данных из БД по значению первичного ключа
        """

        sql = db.select_str(cls._table_name, where=conditions)
        data = db.execute(sql, parameters=tuple(conditions.values()), fetchone=True)

        if data is None:
            return None

        instance = cls()
        instance.fill(data)

        return instance


    @classmethod
    def load_by(cls, conditions: dict = {}) -> list:
        """
        Загрузка данных по условиям
        """

        sql = db.select_str(cls._table_name, where=conditions)
        data = db.execute(sql, parameters=tuple(conditions.values()), fetchall=True)

        for el in data:
            del el['likes']

        return data

    def hide_likes(self):
        del self._properties['likes']









