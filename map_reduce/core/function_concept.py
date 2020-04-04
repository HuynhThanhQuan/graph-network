from . import data_source as ds
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AbstractMapReduceFunction:
    def __init__(self):
        pass

    def execute(self, **kwargs):
        pass


class Splitter(AbstractMapReduceFunction):
    def __init__(self):
        super(Splitter, self).__init__()

    def execute(self, **kwargs):
        data_source = kwargs.get('data_source')
        if isinstance(data_source, ds.AbstractDataSourcePointer):
            return data_source.identify_pointer()


class Mapper(AbstractMapReduceFunction):
    def __init__(self):
        super(Mapper, self).__init__()

    def execute(self, **kwargs):
        input_ = kwargs.get('input')
        map_func = kwargs.get('map')
        if isinstance(input_, ds.DataSourceGenerator):
            iterator = iter(input_)
            for i in range(input_.chunks):
                data = next(iterator)
                map_func(data)
        return self


class Shuffle(AbstractMapReduceFunction):
    def __init__(self):
        super(Shuffle, self).__init__()


class Reducer(AbstractMapReduceFunction):
    def __init__(self):
        super(Reducer, self).__init__()