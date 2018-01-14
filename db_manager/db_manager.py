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

        if document is None:
            self.logger.error("[NOTE] The document is None, NOTHING to insert, operation NOT ALLOWED")
            return False

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is None, operation NOT ALLOWED")
            return False

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = Key.default_group.value

        if isinstance(document, list) and len(document) > 0:
            self.logger.debug(str(db) + ", " + str(collection))
            self.mongodb.insert(db=db, collection=collection, document=document)
        elif isinstance(document, list) and len(document) == 0:
            self.logger.error("[NOTE] The document list is empty, NOTHING to insert, operation NOT ALLOWED")
            return False
        elif not isinstance(document, list):
            if Key.node.value in vid_gid_nid:
                nid = vid_gid_nid[Key.node.value]
                if nid == document[Key.id.value]:
                    self.logger.debug(str(db) + ", " + str(collection) + ", " + str(nid))
                    document_list = [document]
                    self.mongodb.insert(db=db, collection=collection, document=document_list)
                else:
                    self.logger.error("[NOTE] The node ID is NOT the document's nid, operation NOT ALLOWED")
                    return False
            else:
                if Key.id.value in document:
                    self.logger.debug(str(db) + ", " + str(collection) + ", " + str(document[Key.id.value]))
                    document_list = [document]
                    self.mongodb.insert(db=db, collection=collection, document=document_list)
                else:
                    self.logger.error("[NOTE] The node ID is NOT Exist, operation NOT ALLOWED")
                    return False
        else:
            self.logger.error("[NOTE] The document is not standard format, operation NOT ALLOWED")
            return False

        return True

    def update(self, vid_gid_nid=None, condition=None, key_value=None):
        """
        update the value of the KEY when documents with matching conditions,
        if the KEY exist, update the key'svalue
        or insert the key
        :param vid_gid_nid:{Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'}
        :param condition:{Key.location.value: "shanghai"}
        :param key_value:exist or new
        :return:None
        """
        self.logger.debug("update")
        if not isinstance(vid_gid_nid, dict):
            self.logger.error("[NOTE] vid_gid_nid is NOT the dic instance, operation NOT ALLOWED")
            return

        if not isinstance(key_value, dict):
            self.logger.error("[NOTE] The key_value is NOT the dic instance, operation NOT ALLOWED")
            return

        if len(key_value) == 0:
            self.logger.error("[NOTE] The key_value is empty, operation NOT ALLOWED")
            return

        if Key.vendor.value in vid_gid_nid:
            db = vid_gid_nid[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The DB is NOT exist, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = None  # Key.default_group.value

        if Key.node.value in vid_gid_nid:
            nid = vid_gid_nid[Key.node.value]
        else:
            self.logger.warning("[NOTE] Update ANY documents that matching conditions")
            nid = None

        self.logger.debug(str(db) + ", " + str(collection) + ", " + str(nid))
        """
        may be other conditions merge nid and condition, issue: #000002
        """
        if nid is not None:
            if condition is not None:
                """
                fixed #000002 merged conditions
                """
                node = {Key.id.value: nid}
                final_conditions = {**node, **condition}
            else:
                final_conditions = {Key.id.value: nid}
        else:
            final_conditions = condition

        self.mongodb.update(db=db, collection=collection, condition=final_conditions, key_value=key_value)

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
            self.logger.error("[NOTE] The DB is NOT exist, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid:
            collection = vid_gid[Key.group.value]
        else:
            collection = None  # Key.default_group.value

        self.logger.debug(str(db) + ", " + str(collection) + ", " + str(condition))
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
            self.logger.error("[NOTE] The DB is NOT exist, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            collection = None  # Key.default_group.value

        if Key.node.value in vid_gid_nid:
            nid = vid_gid_nid[Key.node.value]
        else:
            nid = None

        self.logger.debug(str(db) + ", " + str(collection) + ", " + str(nid))
        result = self.mongodb.query(db=db, collection=collection, node=nid, condition=condition)
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
            self.logger.error("[NOTE] The DB source is NOT exist, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid_src:
            collection_src = vid_gid_src[Key.group.value]
        else:
            self.logger.error("[NOTE] The collection source is None, operation NOT ALLOWED")
            return

        if Key.vendor.value in vid_gid_des:
            db_des = vid_gid_des[Key.vendor.value]
        else:
            self.logger.error("[NOTE] The target DB is None, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid_des:
            collection_des = vid_gid_des[Key.group.value]
        else:
            collection_des = Key.default_group.value

        """
          query documents with matching conditions
        """
        result = self.query({Key.vendor.value: db_src, Key.group.value: collection_src}, condition=condition)
        """
          fetch and insert the documents with matching conditions to the target collection
        """
        if len(result) > 0:
            self.insert({Key.vendor.value: db_des, Key.group.value: collection_des}, result)
            """
            remove documents with matching conditions
            """
            self.remove({'vendor': db_src, 'group': collection_src}, condition=condition)
        else:
            self.logger.error("[NOTE] query with matching conditions is empty, operation NOT NEED")

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
            self.logger.error("[NOTE] The DB is NOT exist, operation NOT ALLOWED")
            return

        if Key.group.value in vid_gid_nid:
            collection = vid_gid_nid[Key.group.value]
        else:
            self.logger.warning("[NOTE] remove db")
            """
            remove the whole database, issue: #000001
            self.mongodb.remove_db(db=db)  # ????
            return
            """
            collection = None

        if Key.node.value in vid_gid_nid:
            nid = vid_gid_nid[Key.node.value]
            self.logger.debug(str(db) + ", " + str(collection) + ", " + str(nid))
            self.mongodb.remove_one(db=db, collection=collection, node=nid)
            return
        else:
            self.logger.debug(str(db) + ", " + str(collection) + ", " + str(condition))
            self.mongodb.remove_collection(db=db, collection=collection, condition=condition)
            return

    def close(self):
        """
        disconnect the database from host
        :return: None
        """
        self.logger.debug("close")
        self.mongodb.close()
