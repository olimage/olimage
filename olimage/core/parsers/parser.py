import os

import cerberus
import yaml

import olimage.environment as env


class LoaderBase(object):
    def __iter__(self):
        self._iter = iter(self._objects)
        return self

    def __next__(self):
        return next(self._iter)

    def __getitem__(self, item):
        return self._objects[item]

    def __len__(self):
        return len(self._objects)


class GenericLoader(LoaderBase):
    def __init__(self, name, holder, prefix=None) -> None:
        # Hold objects
        self._objects = []

        # Read configuration file
        with open(os.path.join(
                env.paths['configs'],
                '{}'.format(prefix if prefix else ""),
                '{}.yaml'.format(name)
        )) as f:
            data = yaml.full_load(f.read())

        # Load schema
        schemas_dir = os.path.join(env.paths['configs'], 'schemas')
        schema = None

        for (_, _, files) in os.walk(schemas_dir):
            for file in files:
                if file == '{}.yaml'.format(name):
                    with open(os.path.join(schemas_dir, '{}.yaml'.format(name))) as f:
                        schema = yaml.full_load(f.read())

        if schema:
            # Validate config
            v = cerberus.Validator()
            if not v.validate(data, schema):
                raise Exception("Failed to parse \"{}.yaml\": {}".format(name, v.errors))

        # Generate objects
        for key, value in data[name].items():
            self._objects.append(holder(key, value))


class Parser(object):
    """
    Generic class for configuration mapping
    """
    def __init__(self, name: str, data: dict):
        """
        Initialize generic config object

        :param name: config name
        :param data: config data
        """
        self._name = name
        self._data = data

    def __str__(self):
        return self._name

    def __getattr__(self, item):
        # Check if item is in the config dict
        if item not in self._data:
            raise AttributeError("\'{}\' object has no attribute \'{}\'".format(self.__class__.__name__, item))

        # If data[item] is dictionary create new ORM object
        if isinstance(self._data[item], dict):
            return Parser(item, self._data[item])

        # Return value
        return self._data[item]
