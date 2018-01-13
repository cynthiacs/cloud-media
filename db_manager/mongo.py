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
        self._db_collection.insert_one(document)

    def update(self, db=None, collection=None, condition=None, key=None, value=None):
        """
        update documents with matching conditions
        :param db:
        :param collection:
        :param condition:
        :param key:
        :param value:
        :return:
        """
        self._db = self.db_clint[db]
        self._db_collection = self._db[collection]
        self._db_collection.update(condition, {"$set": {key: value}}, multi=True)

    def count(self, db=None, collection=None, condition=None):
        """
        count with matching conditions
        :param db:
        :param collection:
        :param condition:
        :return:
        """
        self._db = self.db_clint[db]
        self._db_collection = self._db[collection]
        if condition is None:
            result = self._db_collection.count()
        else:
            result = self._db_collection.count(condition)
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
        self._db_collection = self._db[collection]
        if node is None:
            result = self._db_collection.find(condition)
        else:
            result = self._db_collection.find({Key.id.value: node}, condition)
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
        for i in self._db_collection.find():
            print(i)

    def remove_collection(self, db=None, collection=None, condition=None):
        """
        remove documents with conditions
        :param db:
        :param collection:
        :param condition:
        :return:
        """
        self._db = self.db_clint[db]
        self._db_collection = self._db[collection]
        if condition is None:
            self._db_collection.drop()
        else:
            self._db_collection.remove(condition)

        for i in self._db_collection.find():
            print(i)

    def remove_db(self, db=None):
        """
        remove database
        :param db:
        :return:
        """
        self._db = self.db_clint[db]
        self._db.drop()

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
