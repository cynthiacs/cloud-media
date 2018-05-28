from pymongo import MongoClient
from db_manager.key import Key


class MongoDB(object):
    """
    MongoDB class:
    mongodb operation
    """

    def __init__(self, host=None, port=None):
        self.db_clint = MongoClient(host, port)
        self._db = None
        self._db_collection = None

    def insert(self, db=None, collection=None, document=None):
        """
        mongodb insert document
        :param db:
        :param collection:
        :param document:
        :return:
        """
        self._db = self.db_clint[db]
        self._db_collection = self._db[collection]
        self._db_collection.insert_many(document)

    def update(self, db=None, collection=None, condition=None, key_value=None):
        """
        update documents with matching conditions
        :param db:
        :param collection:
        :param condition:
        :param key_value:
        :return:
        """
        self._db = self.db_clint[db]
        if collection is not None:
            self._db_collection = self._db[collection]
            if condition is None:
                self._db_collection.update({}, {"$set": key_value}, multi=True)
            else:
                self._db_collection.update(condition, {"$set": key_value}, multi=True)
        else:
            collection_list = self._db.collection_names()
            if len(collection_list) > 0:
                for coll in collection_list:
                    self._db_collection = self._db[coll]
                    if condition is None:
                        self._db_collection.update({}, {"$set": key_value}, multi=True)
                    else:
                        self._db_collection.count(condition, {"$set": key_value}, multi=True)

    def count(self, db=None, collection=None, condition=None):
        """
        count with matching conditions
        :param db:
        :param collection:
        :param condition:
        :return:
        """
        self._db = self.db_clint[db]
        if collection is not None:
            self._db_collection = self._db[collection]
            if condition is None:
                result = self._db_collection.count()
            else:
                result = self._db_collection.count(condition)
            return result
        else:
            collection_list = self._db.collection_names()
            result = 0
            if len(collection_list) > 0:
                for coll in collection_list:
                    self._db_collection = self._db[coll]
                    if condition is None:
                        result_condition = self._db_collection.count()
                    else:
                        result_condition = self._db_collection.count(condition)
                    result += result_condition
                return result
            else:
                return result

    def query(self, db=None, collection=None, node=None, condition=None):
        """
        query documents with matching conditions
        :param db:
        :param collection:
        :param node:
        :param condition:
        :return:
        """
        self._db = self.db_clint[db]
        result = []
        if collection is not None:
            self._db_collection = self._db[collection]
            if condition is not None:
                if node is None:
                    result = self._db_collection.find(condition)
                else:
                    result = self._db_collection.find({Key.id.value: node}, condition)
                return result
            else:
                if node is None:
                    result = self._db_collection.find()
                else:
                    result = self._db_collection.find({Key.id.value: node})
                return result
        else:
            collection_list = self._db.collection_names()
            if len(collection_list) > 0:
                for coll in collection_list:
                    self._db_collection = self._db[coll]
                    if condition is None:
                        result_condition = self._db_collection.find()
                    else:
                        result_condition = self._db_collection.find(condition)
                    result += result_condition
                return result
            else:
                return result

    def remove_one(self, db=None, collection=None, node=None):
        """
        remove one document with nodeID
        :param db:
        :param collection:
        :param node:
        :return:
        """
        self._db = self.db_clint[db]
        self._db_collection = self._db[collection]
        self._db_collection.remove({Key.id.value: node}, False)

    def remove_collection(self, db=None, collection=None, condition=None):
        """
        remove documents with conditions
        :param db:
        :param collection:
        :param condition:
        :return:
        """
        self._db = self.db_clint[db]
        if collection is not None:
            self._db_collection = self._db[collection]
            if condition is None:
                self._db_collection.drop()
            else:
                self._db_collection.remove(condition)
        else:
            collection_list = self._db.collection_names()
            if len(collection_list) > 0:
                for coll in collection_list:
                    self._db_collection = self._db[coll]
                    if condition is None:
                        self._db_collection.drop()
                    else:
                        self._db_collection.remove(condition)
            else:
                return

    def remove_db(self, db=None):
        """
        remove database
        :param db:
        :return:
        """
        self.db_clint.drop_database(db)

    def get_db_list(self):
        """
        :return: get mongodb client database list
        """
        return self.db_clint.list_database_names()

    def close(self):
        """
        disconnect the host database
        :return:
        """
        try:
            if self.db_clint is not None:
                self.db_clint.close()
        except BaseException as e:
            print("MongoDB close failed." + str(e))
