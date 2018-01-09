from pymongo import MongoClient


class CollectionOnLine(object):
    def __init__(self, url='mongodb://139.224.128.15'):
        self._db_client = MongoClient(url)
        self._db = self._db_client.extmqtt_nodes
        self._db_col_nodes_online = self._db.nodes_online

    def remove(self, node_id):
        if self._db_col_nodes_online.find_one({'id': node_id}) is not None:
            print("[DB] remove: " + node_id)
            self._db_col_nodes_online.remove({'id': node_id})

    def insert(self, params):
        print("[DB] insert %s" % params)
        self._db_col_nodes_online.insert_one(params)

    def find_all(self):
        nodes_online = self._db_col_nodes_online.find()
        # NOTE: this works, but str(list(car_online)) wont
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find_role(self, role):
        nodes_online = self._db_col_nodes_online.find({"role": role})
        l_nodes_online = list(nodes_online)
        return str(l_nodes_online)

    def find(self, filter_param):
        """
        :param filter_param:
        :return: string to transfer by mqtt
        """
        # find return Cursor instance which can be interate over all mathing document
        find_result = self._db_col_nodes_online.find(filter_param)
        # convert into list, take care about the memory when using this !!
        l_find_result = list(find_result)
        return str(l_find_result)

    def find_one(self, filter_param):
        """
        :param filter_param:
        :return:  return the first match, and the result is dict
        """
        return self._db_col_nodes_online.find_one(filter_param)

    def update(self, node_id, filed, value):
        print("[DB] update " + node_id)
        print("\t(" + filed + ":" + value + ")")
        self._db_col_nodes_online.update_one({"id": node_id}, {'$set': {filed: value}})

    def online(self, node_id, params):
        self.remove(node_id)
        self.insert(params=params)

    def offline(self, node_id):
        self.remove(node_id)


class OnlineNodes(object):
    """
    add(vid_gid_nid, {k: v, ....})
    delete(vid_gid_nid)
    find({k: v, ...})  key: vid, gid, nid, role....
    update(vid_gid_nid, field, value)
    count({k: v, ...})
    """
    def __init__(self, url='mongodb://139.224.128.15'):
        self._db_client = MongoClient(url)
        self._db = self._db_client.extmqtt_nodes
        self._db_col_nodes_online = self._db.nodes_online
        pass

    def add(self, vid_gid_nid, jparams):
        vid, gid, nid = vid_gid_nid.split('_')
        self._remove(nid)
        self._insert(jparams)

    def delete(self, vid_gid_nid):
        vid, gid, nid = vid_gid_nid.split('_')
        self._remove(nid)

    def find(self, jparams):
        # find return Cursor instance which can be interate over all mathing document
        find_result = self._db_col_nodes_online.find(jparams)
        # convert into list, take care about the memory when using this !!
        l_find_result = list(find_result)
        return str(l_find_result)

    def update(self, vid_gid_nid, field, value):
        pass

    def _remove(self, nid):
        if self._db_col_nodes_online.find_one({'id': nid}) is not None:
            print("[DB] remove: " + nid)
            self._db_col_nodes_online.remove({'id': nid})

    def _insert(self, jparams):
        print("[DB] insert %s" % jparams)
        self._db_col_nodes_online.insert_one(jparams)
