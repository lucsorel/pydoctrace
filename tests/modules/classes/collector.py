class Collector:
    def __init__(self, values, aggregator):
        self.values = values
        self.aggregator = aggregator

    def _aggregate(self):
        return self.aggregator(self.values)

    def _diff(self, aggregation, expected_result):
        raise NotImplementedError

    def collect(self, expected_result):
        aggregation = self._aggregate()
        return self._diff(aggregation, expected_result)

    @classmethod
    def collector_factory(cls, values, aggregator, expected_result):
        processor = cls(values, aggregator)
        return processor.collect(expected_result)
