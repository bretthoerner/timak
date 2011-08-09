=====
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

Why?
----

I needed *highly available*, *linearly scalable* timelines where readers and writers *don't block* one another. Because Riak is a Dynamo based system, multiple writers can update a single value and I can merge the conflicts on a later read. I can also add a machine to the cluster for more throughput, and since it's simply fetching denormalized timelines by key it should be incredibly performant.

So what? I could write this in...
---------------------------------

PostgreSQL or MySQL
```````````````````

This would be a very simple table in a RDBMS. It could even be boundless (though without some PLSQL hackery large OFFSETS are very expensive). You'd be hitting large indexes instead of fetching values directly by key. The biggest problem is it all has to fit on a single system, unless you manually shard the data (and re-shard if you ever grew out of that size). Plus you'd have to deal with availability using read slaves and failover.

MongoDB
```````

The only possible difference I see from the RDBMSs above is that you could use auto-sharding. If that's your thing, and you trust it, then it may work fine for this.

Redis
`````

You can fake timelines in Redis using a list or sorted set. Like RDBMS you have to handle all of the sharding yourself, re-shard on growth, and use slaves and failaover for availability. In addition to these, and even more critical for my use case: all of your timelines would have to fit in RAM. If you have this problem and that kind of money please send me some.

Cassandra
`````````

Probably another great fit. You could even store much longer timelines, though I'm not sure what the cost is of doing an ORDER_BY/OFFSET equivalent on the columns in a Cassandra row.


TODO
----

1. Add better API with cursors (last seen ``obj_date``?) for pagination.
2. Built-in Django support for update on ``post_save`` and ``post_delete``.
3. Compress values.

