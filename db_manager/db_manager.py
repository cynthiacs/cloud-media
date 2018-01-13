from db_manager.mongo import MongoDB
from db_manager.key import Key
import logging
import logging.config


class DBManager(object):
    """
    DBManager:
    support external database manager
    @:parameter host:127.0.0.1
    @:parameter port:27017
    """

    def __init__(self, host=None, port=None):
        self.mongodb = MongoDB(host, port)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(name)s: %(levelname)-4s %(filename)s [line: %(lineno)d] [funtion: %(funcName)s] %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('DBManager').addHandler(console)
        self.logger = logging.getLogger('DBManager')

    def insert(self, vid_gid_nid=None, document=None):
        """
        insert documents to the target collection
        :param vid_gid_nid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'}
        :param document:{Key.id.value: "001", Key.nick.value: "Ronald", Key.role.value: 'pusher',
                               Key.time.value: "male"}
        :return:True;False
        """
        self.logger.debug("insert")
        if not isinstance(vid_gid_nid, dict):
            self.logger.error("[NOTE] vid_gid_nid is NOT the dic instance")
            return False

        if not isinstance(document, dict):
            self.logger.error("[NOTE] document is NOT the dic instance")
            return False

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, Stopping operation")
            return False

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = Key.default_group.value

        if Key.node.value in vid_gid_nid:
            node = vid_gid_nid[Key.node.value]
        else:
            self.logger.error("[NOTE] The node ID is None, Stopping operation")
            return False

        if node != document[Key.id.value]:
            self.logger.error("[NOTE] The node ID is NOT the document's nodeID, Insert Database NOT ALLOWED")
            return False

        self.logger.debug(db + ", " + collection + ", " + node)
        self.mongodb.insert(db=db, collection=collection, document=document)
        return True

    def update(self, vid_gid_nid=None, condition=None, key=None, value=None):
        """
        update the value of the KEY when documents with matching conditions,
        if the KEY exist, update the key'svalue
        or insert the key
        :param vid_gid_nid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'}
        :param condition:{Key.location.value: "shanghai"}
        :param key: exist or new
        :param value: update or insert
        :return:None
        """
        self.logger.debug("update")
        if not isinstance(vid_gid_nid, dict):
            self.logger.error("[NOTE] vid_gid_nid is NOT the dic instance")
            return

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, Stopping operation")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = Key.default_group.value

        if Key.node.value in vid_gid_nid:
            node = vid_gid_nid[Key.node.value]
        else:
            self.logger.warning("[NOTE] Update ANY documents that matching conditions")
            node = None

        self.logger.debug(db + ", " + str(collection) + ", " + str(node))
        """
        may be other conditions merge nodeID and condition, issue: #000002
        """
        if node is not None:
            final_conditions = {Key.id.value: node}  # + condition
        else:
            final_conditions = condition
        self.mongodb.update(db=db, collection=collection, condition=final_conditions, key=key, value=value)

    def count(self, vid_gid=None, condition=None):
        """
        count documents with matching conditions in one collection
        :param vid_gid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'}
        :param condition:{"location": "shanghai"}
        :return:count
        """
        self.logger.debug("count")
        if not isinstance(vid_gid, dict):
            self.logger.error("[NOTE] vid_gid is NOT the dic instance")
            return

        if Key.vendor.value in vid_gid:
            db = vid_gid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, Stopping operation!")
            return

        if Key.group.value in vid_gid:
            collection = vid_gid[Key.group.value]
        else:
            collection = Key.default_group.value

        self.logger.debug(db + ", " + collection + ", " + str(condition))
        return self.mongodb.count(db, collection, condition)

    def query(self, vid_gid_nid=None, condition=None):
        """
        query documents with matching conditions
        :param vid_gid_nid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'}
        :param condition:condition={"location": "shanghai"}
        :return:documents list
        """
        self.logger.debug("query")
        if not isinstance(vid_gid_nid, dict):
            self.logger.error("[NOTE] vid_gid_nid is NOT the dic instance")
            return

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, Stopping operation")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = Key.default_group.value

        if Key.node.value in vid_gid_nid:
            node = vid_gid_nid[Key.node.value]
        else:
            node = None

        self.logger.debug(db + ", " + collection + ", " + str(node))
        result = self.mongodb.query(db=db, collection=collection, node=node, condition=condition)
        return list(result)

    def move(self, vid_gid_src=None, vid_gid_des=None, condition=None):
        """
        move documents with matching conditions from source collection(vid_gid_src) to target collection(vid_gid_des)
        :param vid_gid_src:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'}
        :param vid_gid_des:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupB'}
        :param condition:{"location": "shanghai"}
        :return:None
        """
        self.logger.debug("move")
        if Key.vendor.value in vid_gid_src:
            db_src = vid_gid_src[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB source is NOT exist, Stopping operation")
            return

        if Key.group.value in vid_gid_src:
            collection_src = vid_gid_src[Key.group.value]
        else:
            self.logger.error("[NOTE] The collection source is None, Stopping operation")
            return

        db_des = vid_gid_des[Key.vendor.value]
        collection_des = vid_gid_des[Key.group.value]

        """
          query documents with matching conditions
        """
        result = self.query({Key.vendor.value: db_src, Key.group.value: collection_src}, condition=condition)
        """
          fetch and insert the documents with matching conditions to the target collection
        """
        for i in result:
            nid = i[Key.id.value]
            self.insert({Key.vendor.value: db_des, Key.group.value: collection_des, Key.node.value: nid}, i)
        """
          remove documents with matching conditions
        """
        self.remove({'vendor': db_src, 'group': collection_src}, condition=condition)

    def remove(self, vid_gid_nid=None, condition=None):
        """
        remove document with matching conditions
        :param vid_gid_nid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'}
        :param condition:{"id": "002"}
        :return:None
        """
        self.logger.debug("remove")
        if not isinstance(vid_gid_nid, dict):
            self.logger.error("[NOTE] vid_gid_nid is NOT the dic instance")
            return

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, Stopping operation")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            self.logger.warning("[NOTE] remove db")
            """
            remove the whole database, issue: #000001
            """
            self.mongodb.remove_db(db=db)  # ????
            return

        if Key.node.value in vid_gid_nid:
            node = vid_gid_nid[Key.node.value]
            self.logger.debug(db + ", " + collection + ", " + node)
            self.mongodb.remove_one(db=db, collection=collection, node=node)
            return
        else:
            self.mongodb.remove_collection(db=db, collection=collection, condition=condition)
            return

    def close(self):
        """
        disconnect the database from host
        :return: None
        """
        self.logger.debug("close")
        self.mongodb.close()
