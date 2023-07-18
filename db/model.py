from db_api.provider import select_str, execute, insert_str, update_str, delete_str


class Model:
    _pk = None  # Название столбца, содержащего первичный ключ
    _table_name = ""  # Название таблицы, с которой связана модель
    _parameters = {}  # Словарь параметров, с которыми работает модель

    def init(self):
        self._check_database_attributes()

        self._modified = False
        self._modified_properties = {}
        self._properties = {}

        self.fill({})

    def getattr(self, key):
        if key not in self._properties:
            raise Exception(f"Property {key} does not exists")

        return self._properties.get(key)

    def setattr(self, key, value):
        super().setattr(key, value)

        if not self.dict.get('_properties'):
            self.dict['_properties'] = {}

        if key in self._properties:
            if not self._modified_properties.get(key):
                self._modified_properties[key] = {'from': self._properties[key]}

            self._modified_properties[key]['to'] = value
            self._properties[key] = value
            self._modified = True

    def get_pk(self) -> str:
        """
        Получить столбец, содержащий первичный ключ
        """
        return self._pk

    def get_pk_value(self):
        """
        Получить значение первичного ключа
        """
        return self._properties.get(self._pk)

    def fill(self, data: dict):
        """
        Наполнение модели данными
        """
        for parameter in self._parameters:
            self._properties[parameter] = data.get(parameter, None)

    def get_pseudo(self, field_name) -> str | None:
        """
        Получить псевдоним параметра
        """
        if field_name not in self._parameters:
            return None

        return self._parameters[field_name].get('pseudo')

    def _check_database_attributes(self):
        """
        Проверка заполненности аттрибутов модели
        """
        if not self._pk:
            raise Exception("Primary key for model is not defined")

        if not self._table_name:
            raise Exception("Table name for model is not defined")

    @classmethod
    def load_by(cls, conditions: dict) -> list:
        """
        Загрузка данных по условиям
        """
        cls._check_database_attributes(cls)

        sql = select_str(cls._table_name, cls._parameters.keys(), where=conditions)
        data = execute(sql, parameters=tuple(conditions.values()), fetchall=True)
        result = []

        for i in data:
            instance = cls()
            instance.fill(i)
            result.append(instance)

        return result

    @classmethod
    def load(cls, pk_value):
        """
        Загрузка данных из БД по значению первичного ключа
        """
        cls._check_database_attributes(cls)

        sql = select_str(cls._table_name, cls._parameters.keys(), where={cls._pk: pk_value})
        data = execute(sql, parameters=(pk_value,), fetchone=True)

        if data is None:
            return None

        instance = cls()
        instance.fill(data)

        return instance

    def delete(self):
        """
        Удаление записи из БД
        """
        pk = self.get_pk_value()
        if pk is None:
            return

        sql = delete_str(self._table_name, where={self._pk: pk})
        execute(sql, parameters=(pk,), commit=True)

        self.fill({})
        self._modified = False
        self._modified_properties = {}

    def save(self):
        """
        Сохранение изменений в БД
        """
        if self._modified is False:
            return

        params = dict(self._properties)
        del params[self.get_pk()]

        self._validate_properties()

        pk = self.get_pk_value()
        if pk is None:
            # Если значения первичного ключа нет, значит запись новая, нужна вставка
            sql = insert_str(self._table_name, params)
            result = execute(sql, tuple(params.values()), commit=True, lastrowid=True)
            self._properties[self._pk] = result
        else:
            # Если значение первичного ключа есть, делаем обновление записи
            sql = update_str(self._table_name, params, where={self._pk: pk})
            vals = list(params.values())
            vals.append(pk)
            execute(sql, tuple(vals), commit=True)

        self._modified = False
        self._modified_properties = {}

    def update(self, values: dict):
        for k in values.keys():
            self.setattr(k, values.get(k))

        return self

    def get_modified_properties(self) -> dict:
        """
        Получение всех свойств, которые были изменены в процессе работы
        """
        return dict(self._modified_properties)

    def _validate_properties(self):
        for property in self._properties:
            self._validate_property(property)

    def _validate_property(self, property_name):
        validators = self._parameters[property_name].get('validators')
        if not validators:
            return

        for validator in validators:
            # Проверка поля на возможность изменения
            if validator == "ReadOnly" and self._modified_properties.get(property_name):
                raise Exception(f"Property {property_name} is immutable")

            # Проверка поля на обязательность заполнения
            if validator == "Required" and not self._properties[property_name]:
                raise Exception(f"Property {property_name} is required")

    def keys(self):
        return list(self._properties.keys())

    def getitem(self, key):
        return self._properties[key]