from map_reduce.core.function_concept import AbstractMapReduceFunction
import logging
from . import data_source as ds
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MapReducePipeLine:
    def __init__(self, splitter=None, mapper=None, shuffle=None, reducer=None):
        self.splitter = splitter
        self.mapper = mapper
        self.shuffle = shuffle
        self.reducer = reducer
        self._check_variable_types_()

    def _check_variable_types_(self):
        assert isinstance(self.splitter, AbstractMapReduceFunction), "Splitter must be instance of " \
                                                                     "AbstractMapReduceFunction "
        assert isinstance(self.mapper, AbstractMapReduceFunction), "Mapper must be instance of " \
                                                                   "AbstractMapReduceFunction "
        assert isinstance(self.shuffle, AbstractMapReduceFunction), "Shuffle must be instance of " \
                                                                    "AbstractMapReduceFunction "
        assert isinstance(self.reducer, AbstractMapReduceFunction), "Reducer must be instance of " \
                                                                    "AbstractMapReduceFunction "

    def transform(self, data_source):
        assert isinstance(data_source, ds.AbstractDataSource), "Data Source must be instance of AbstractDataSource"
        splitted_input = self.splitter.execute({'data_source': data_source})
        assert splitted_input is not None, "Cannot split data source or invalid operation"
        mapped = self.mapper.execute({'input': splitted_input})


class MapReduceExecution:
    def __init__(self, data_source, mapreduce_pipeline, output_aggregator):
        self.data_source = data_source
        self.mapreduce_pipeline = mapreduce_pipeline
        self.output_aggregator = output_aggregator
        self._check_variable_types_()

    def _check_variable_types_(self):
        assert isinstance(self.mapreduce_pipeline, MapReducePipeLine), "Map Reduce Pipele must be instance of " \
                                                                       "MapReducePipeLine "

    def run(self):
        self.mapreduce_pipeline.transform(self.data_source)