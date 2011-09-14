import datetime


class Timeline(object):
    def __init__(self, connection=None, bucket="timelines", order='desc',
                 max_items=1000):
        self.connection = connection
        self.bucket = bucket
        self.order = order
        self.max_items = max_items

    def get_connection(self):
        return self.connection

    def get_bucket(self):
        return self.connection.bucket(self.bucket)

    def _datetime_to_js(self, dt):
        return int(dt.strftime("%s") + dt.strftime("%f")[:3])

    def _merge_two(self, obj1, obj2):
        """
        Merges two data dictionaries, respecting the one with the most recent
        modified time per item.
        """
        for uniq_ident in obj2.keys():
            if (uniq_ident not in obj1) \
               or (obj1[uniq_ident]['modified'] \
                   < obj2[uniq_ident]['modified']):
                obj1[uniq_ident] = obj2[uniq_ident]

        return obj1 # self._dict_to_list(obj1)

    def _list_to_dict(self, l):
        if not l: return {}
        d = {}
        for o in l:
            d[o['id']] = o
        return d

    def _dict_to_list(self, d):
        if not d: return []
        l = d.values()
        reverse = self.order == 'desc'
        l.sort(key=lambda x: x['score'], reverse=reverse)
        return l

    def _list_to_data(self, l):
        """
        Coerces a list of timeline objects into the data the user cares about.
        """
        return [o.get('data', None) or o.get('id')
                for o in l
                if not o.get('deleted', False)]

    def _get_obj_and_data(self, key, write_merged=True):
        """
        Returns RiakObject with proper vclock set and dictionary of merged entries.

        NOTE: The data on the object itself should not be used, the object is
        returned only so it can be used later for updates.
        """
        bucket = self.get_bucket()

        obj = bucket.get(key)
        data = [self._list_to_dict(o.get_data()) for o
                in obj.get_siblings()
                if o.get_data() is not None]

        obj_data = obj.get_data()
        if obj_data is not None:
            data.append(self._list_to_dict(obj_data))

        # if we have no data or only 1 sibling we can safetly return
        # it without merging
        if len(data) == 0:
            return obj, {}
        elif len(data) == 1:
            return obj, data[0]

        resolved_data = reduce(self._merge_two, data)
        # NOTE: is this really the only way to fix a conflict in the
        # python riak library?
        try:
            obj._vclock = obj.get_sibling(0).vclock()
        except IndexError:
            pass
        else:
            if write_merged:
                obj.set_data(self._dict_to_list(resolved_data)[:self.max_items])
                obj.store()

        return obj, resolved_data

    def get(self, key, raw=False):
        """
        Returns timeline as list.
        """
        # TODO: Optimize this so we don't have to coerce
        # list->dict->list for the common case.
        result = self._dict_to_list(self._get_obj_and_data(key)[1])
        if raw:
            return result
        return self._list_to_data(result)

    def _make_op(action):
        assert action in ('add', 'delete')
        def _op(self, key, uniq_ident, obj_score, obj_data=None, raw=False):
            now = self._datetime_to_js(datetime.datetime.utcnow())
            obj, data = self._get_obj_and_data(key, write_merged=False)

            if isinstance(obj_score, datetime.datetime):
                obj_score = self._datetime_to_js(obj_score)

            new_item = {'id': uniq_ident,
                        'score': obj_score,
                        'modified': now}
            if obj_data:
                new_item['data'] = obj_data
            if action == 'delete':
                new_item['deleted'] = True

            existing = data.get(uniq_ident, None)
            if existing:
                if existing['modified'] < now:
                    data[uniq_ident] = new_item
            else:
                data[uniq_ident] = new_item

            timeline = self._dict_to_list(data)[:self.max_items]
            obj.set_data(timeline)
            obj.store()
            if raw:
                return timeline
            return self._list_to_data(timeline)
        return _op

    add = _make_op("add")
    delete = _make_op("delete")
