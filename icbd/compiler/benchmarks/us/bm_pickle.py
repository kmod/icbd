#!/usr/bin/env python

"""Script for testing the performance of pickling/unpickling.

This will pickle/unpickle several real world-representative objects a few
thousand times. The methodology below was chosen for was chosen to be similar
to real-world scenarios which operate on single objects at a time. Note that if
we did something like

    pickle.dumps([dict(some_dict) for _ in xrange(10000)])

this isn't equivalent to dumping the dict 10000 times: pickle uses a
highly-efficient encoding for the n-1 following copies.
"""

__author__ = "collinwinter@google.com (Collin Winter)"

# Python imports
import datetime
import gc
import optparse
import random
import sys
import time

# Local imports
import util

gc.disable()  # Minimize jitter.

DICT = {
    'ads_flags': 0L,
    'age': 18,
    'birthday': datetime.date(1980, 5, 7),
    'bulletin_count': 0L,
    'comment_count': 0L,
    'country': 'BR',
    'encrypted_id': 'G9urXXAJwjE',
    'favorite_count': 9L,
    'first_name': '',
    'flags': 412317970704L,
    'friend_count': 0L,
    'gender': 'm',
    'gender_for_display': 'Male',
    'id': 302935349L,
    'is_custom_profile_icon': 0L,
    'last_name': '',
    'locale_preference': 'pt_BR',
    'member': 0L,
    'tags': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    'profile_foo_id': 827119638L,
    'secure_encrypted_id': 'Z_xxx2dYx3t4YAdnmfgyKw',
    'session_number': 2L,
    'signup_id': '201-19225-223',
    'status': 'A',
    'theme': 1,
    'time_created': 1225237014L,
    'time_updated': 1233134493L,
    'unread_message_count': 0L,
    'user_group': '0',
    'username': 'collinwinter',
    'play_count': 9L,
    'view_count': 7L,
    'zip': ''}

TUPLE = ([265867233L, 265868503L, 265252341L, 265243910L, 265879514L,
          266219766L, 266021701L, 265843726L, 265592821L, 265246784L,
          265853180L, 45526486L, 265463699L, 265848143L, 265863062L,
          265392591L, 265877490L, 265823665L, 265828884L, 265753032L], 60)


def mutate_dict(orig_dict, random_source):
    new_dict = dict(orig_dict)
    for key, value in new_dict.items():
        rand_val = random_source.random() * sys.maxint
        if isinstance(key, (int, long)):
            new_dict[key] = long(rand_val)
        elif isinstance(value, str):
            new_dict[key] = str(rand_val)
        elif isinstance(key, unicode):
            new_dict[key] = unicode(rand_val)
    return new_dict


random_source = random.Random(5)  # Fixed seed.
DICT_GROUP = [mutate_dict(DICT, random_source) for _ in range(3)]


def test_pickle(num_obj_copies, pickle, options):
    # Warm-up runs.
    pickle.dumps(DICT, options.protocol)
    pickle.dumps(TUPLE, options.protocol)
    pickle.dumps(DICT_GROUP, options.protocol)

    loops = num_obj_copies / 20  # We do 20 runs per loop.
    times = []
    for _ in xrange(options.num_runs):
        t0 = time.time()
        for _ in xrange(loops):
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(DICT, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(TUPLE, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
            pickle.dumps(DICT_GROUP, options.protocol)
        t1 = time.time()
        times.append(t1 - t0)
    return times


def test_unpickle(num_obj_copies, pickle, options):
    pickled_dict = pickle.dumps(DICT, options.protocol)
    pickled_tuple = pickle.dumps(TUPLE, options.protocol)
    pickled_dict_group = pickle.dumps(DICT_GROUP, options.protocol)

    # Warm-up runs.
    pickle.loads(pickled_dict)
    pickle.loads(pickled_tuple)
    pickle.loads(pickled_dict_group)

    loops = num_obj_copies / 20  # We do 20 runs per loop.
    times = []
    for _ in xrange(options.num_runs):
        t0 = time.time()
        for _ in xrange(loops):
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_dict)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_tuple)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
            pickle.loads(pickled_dict_group)
        t1 = time.time()
        times.append(t1 - t0)
    return times


LIST = [[range(10), range(10)] for _ in xrange(10)]


def test_pickle_list(loops, pickle, options):
    # Warm-up runs.
    pickle.dumps(LIST, options.protocol)
    pickle.dumps(LIST, options.protocol)

    loops = loops / 5  # Scale to compensate for the workload.
    times = []
    for _ in xrange(options.num_runs):
        t0 = time.time()
        for _ in xrange(loops):
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
            pickle.dumps(LIST, options.protocol)
        t1 = time.time()
        times.append(t1 - t0)
    return times


def test_unpickle_list(loops, pickle, options):
    pickled_list = pickle.dumps(LIST, options.protocol)

    # Warm-up runs.
    pickle.loads(pickled_list)
    pickle.loads(pickled_list)

    loops = loops / 5  # Scale to compensate for the workload.
    times = []
    for _ in xrange(options.num_runs):
        t0 = time.time()
        for _ in xrange(loops):
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
            pickle.loads(pickled_list)
        t1 = time.time()
        times.append(t1 - t0)
    return times


MICRO_DICT = dict((key, dict.fromkeys(range(10))) for key in xrange(100))

def test_pickle_dict(loops, pickle, options):
    # Warm-up runs.
    pickle.dumps(MICRO_DICT, options.protocol)
    pickle.dumps(MICRO_DICT, options.protocol)

    loops = max(1, loops / 10)
    times = []
    for _ in xrange(options.num_runs):
        t0 = time.time()
        for _ in xrange(loops):
            pickle.dumps(MICRO_DICT, options.protocol)
            pickle.dumps(MICRO_DICT, options.protocol)
            pickle.dumps(MICRO_DICT, options.protocol)
            pickle.dumps(MICRO_DICT, options.protocol)
            pickle.dumps(MICRO_DICT, options.protocol)
        t1 = time.time()
        times.append(t1 - t0)
    return times


if __name__ == "__main__":
    parser = optparse.OptionParser(
        usage="%prog [pickle|unpickle] [options]",
        description=("Test the performance of pickling."))
    parser.add_option("--use_cpickle", action="store_true",
                      help="Use the C version of pickle.")
    parser.add_option("--protocol", action="store", default=2, type="int",
                      help="Which protocol to use (0, 1, 2).")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    benchmarks = ["pickle", "unpickle", "pickle_list", "unpickle_list",
                  "pickle_dict"]
    for bench_name in benchmarks:
        if bench_name in args:
            benchmark = globals()["test_" + bench_name]
            break
    else:
        raise RuntimeError("Need to specify one of %s" % benchmarks)

    if options.use_cpickle:
        num_obj_copies = 8000
        import cPickle as pickle
    else:
        num_obj_copies = 200
        import pickle

    if options.protocol > 0:
        num_obj_copies *= 2  # Compensate for faster protocols.

    util.run_benchmark(options, num_obj_copies, benchmark, pickle, options)
