timak
=====

timak is a Python library for storing timelines (activity streams) in Riak. It is very alpha and rough around the edges.

It is loosely based on my understanding of Yammer's `Streamie <http://blog.basho.com/2011/03/28/Riak-and-Scala-at-Yammer/>`_.

Example
-------

Timelines are unique sets of objects (unique by the ID you provide) ordered by a datetime (that you also provide). They are bounded, so items fall of the end when a (user defined) capacity is reached.

    >>> from datetime import datetime
    >>> import riak
    >>> from timak.timelines import Timeline

    >>> conn = riak.RiakClient()

    >>> tl = Timeline(connection=conn, max_items=3)

    >>> tl.add("brett:tweets", 1, datetime(2011, 1, 1))
    [1]
    >>> tl.add("brett:tweets", 2, datetime(2011, 1, 2))
    [2, 1]
    >>> tl.add("brett:tweets", 3, datetime(2011, 1, 3))
    [3, 2, 1]
    >>> tl.add("brett:tweets", 4, datetime(2011, 1, 4))
    [4, 3, 2]
    >>> tl.delete("brett:tweets", 2, datetime(2011, 1, 2))
    [4, 3]

As you can see the default order is descending by the date you provide, and the object IDs are returned by default. You can also provide an ``obj_data`` argument (JSON serializable) which will be returned instead.

   >>> tl.add("brett:tweets", 5, datetime(2011, 1, 5), obj_data={'body': 'Hello world, this is my first tweet'})
   [{'body': 'Hello world, this is my first tweet'}, 4, 3]


TODO
----

1. Explain why this is special.
2. Go into drawbacks.
3. Add better API with cursors (last seen ``obj_date``?) for pagination.
4. Built-in Django support for update on ``post_save`` and ``post_delete``.
5. Tests, tests, tests.
6. Compress values.

