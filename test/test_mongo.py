
# python -m pip install pymongo
# pip3 install pymongo

from pymongo import MongoClient

if __name__ == '__main__':
    _db_client = MongoClient("mongodb://139.224.128.15")
    _db = _db_client.cars
    _online = _db.car_online.find()

    print(_online)
    for p in _online:
        print(p)
    print("end here....")




