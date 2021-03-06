import importlib
import inspect
import os

import olimage.environment as env

from .apt_cache import AptCache
from .getty import Getty
from .resize import Resize


class ServiceMeta(type):
    def __getattribute__(self, item):

        if env.obj_graph is None:
            return type.__getattribute__(self, item)

        modules = {}
        for (path, dirs, files) in os.walk(os.path.dirname(__file__)):
            # Don't walk subdirectories
            if path != os.path.dirname(__file__):
                continue

            for file in files:
                file = str(file)
                if file.endswith('.py'):
                    module = os.path.splitext(file)[0]

                    if module == '__init__' or module == 'service':
                        continue

                    module_path = 'olimage.core.service.' + module
                    obj = importlib.import_module(module_path)

                    for name, cls in inspect.getmembers(obj, inspect.isclass):
                        if cls.__module__ != module_path:
                            continue

                        modules[module] = cls

        if item in modules:
            return env.obj_graph.provide(modules[item])

        return type.__getattribute__(self, item)


class Service(metaclass=ServiceMeta):
    apt_cache: AptCache
    getty: Getty
    resize: Resize