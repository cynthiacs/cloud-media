from pymongo import MongoClient
from db_manager.db_manager import DBManager
from db_manager.key import Key


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
    def __init__(self, url='139.224.128.15', port=27017):
        self._db_manager = DBManager(host=url, port=port)

    def find_one(self, source_tag):
        """

        :param source_tag:
        :return: a dic
        """
        vid, gid, nid = source_tag.split('_')
        node_info = self._db_manager.query(
            vid_gid_nid={Key.vendor.value: vid, Key.group.value: gid, Key.node.value: nid})
        if len(node_info) == 0:
            return None
        else:
            return node_info[0]

    def find_role(self, source_tag, role):
        vid, gid, nid = source_tag.split('_')
        role_info = self._db_manager.query(
            vid_gid_nid={Key.vendor.value: vid, Key.group.value: gid},
            condition={Key.role.value: role})
        return role_info
        #return str(role_info)

    def insert(self, source_tag, document):
        vid, gid, nid = source_tag.split('_')
        self._db_manager.insert(
            vid_gid={Key.vendor.value: vid, Key.group.value: gid},
            document=document
        )

    def remove(self, source_tag):
        vid, gid, nid = source_tag.split('_')
        self._db_manager.remove(
            vid_gid_nid={Key.vendor.value: vid, Key.group.value: gid, Key.node.value: nid})

    def update(self, source_tag, field, value):
        vid, gid, nid = source_tag.split('_')
        self._db_manager.update(
            vid_gid_nid={Key.vendor.value: vid, Key.group.value: gid, Key.node.value: nid},
            key_value={field: value}
        )

