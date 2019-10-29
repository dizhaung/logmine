import collections
import itertools
import multiprocessing


class MapReduce:

    def __init__(self, map_func, reduce_func, num_workers=None):
        """
        map_func

          Function to map inputs to intermediate data. Takes as
          argument one input value and returns a tuple with the
          key and a value to be reduced.

        reduce_func

          Function to reduce partitioned version of intermediate
          data to final output. Takes as argument a key as
          produced by map_func and a sequence of the values
          associated with that key.

        num_workers

          The number of workers to create in the pool. Defaults
          to the number of CPUs available on the current host.
        """
        self.map_func = map_func
        self.reduce_func = reduce_func
        self.pool = multiprocessing.Pool(num_workers)

    def partition(self, mapped_values):
        """Organize the mapped values by their key.
        Returns an unsorted sequence of tuples with a key
        and a sequence of values.
        """
        partitioned_data = collections.defaultdict(list)
        for key, value in mapped_values:
            partitioned_data[key].append(value)
        return partitioned_data.items()

    def __call__(self, inputs, chunksize=1):
        """Process the inputs through the map and reduce functions
        given.

        inputs
          An iterable containing the input data to be processed.

        chunksize=1
          The portion of the input data to hand to each worker.
          This can be used to tune performance during the mapping
          phase.
        """
        map_responses = self.pool.map(
            self.map_func,
            inputs,
            chunksize=chunksize,
        )
        partitioned_data = self.partition(
            itertools.chain(*map_responses)
        )
        reduced_values = self.pool.map(
            self.reduce_func,
            partitioned_data,
        )
        return reduced_values
#
#
# def file_to_words(filename):
#     """Read a file and return a sequence of
#     (word, occurences) values.
#     """
#     STOP_WORDS = set([
#         'a', 'an', 'and', 'are', 'as', 'be', 'by', 'for', 'if',
#         'in', 'is', 'it', 'of', 'or', 'py', 'rst', 'that', 'the',
#         'to', 'with',
#     ])
#
#     print('{} reading {}'.format(
#         multiprocessing.current_process().name, filename))
#     output = []
#
#     with open(filename, 'rt') as f:
#         for line in f:
#             # Skip comment lines.
#             if line.lstrip().startswith('..'):
#                 continue
#             for word in line.split():
#                 word = word.lower()
#                 if word.isalpha() and word not in STOP_WORDS:
#                     output.append((word, 1))
#     return output
#
#
# def count_words(item):
#     """Convert the partitioned data for a word to a
#     tuple containing the word and the number of occurences.
#     """
#     word, occurences = item
#     return (word, sum(occurences))
#
#
# if __name__ == '__main__':
#     import operator
#     import glob
#
#     input_files = glob.glob('*.rst')
#
#     mapper = MapReduce(file_to_words, count_words)
#     word_counts = mapper(input_files)
#     word_counts.sort(key=operator.itemgetter(1))
#     word_counts.reverse()
#
#     print('\nTOP 20 WORDS BY FREQUENCY\n')
#     top20 = word_counts[:20]
#     longest = max(len(word) for word, count in top20)
#     for word, count in top20:
#         print('{word:<{len}}: {count:5}'.format(
#             len=longest + 1,
#             word=word,
#             count=count)
#         )