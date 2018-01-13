from db_manager.db_manager import DBManager
from db_manager.key import Key
import time


def _current_time_():
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return date


def _merge_(param=None):
    d1 = {'id': '001', 'date': 'mmm'}
    d2 = {**d1, **param}
    print("MERGE" + str(d2))


if __name__ == '__main__':
    print("test_DB")
    dbManager = DBManager(host='127.0.0.1', port=27017)

    dbManager.remove({Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    dbManager.remove({Key.vendor.value: 'VendorA', Key.group.value: 'GroupB'})
    dbManager.insert(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'},
                     document={Key.id.value: "001", Key.nick.value: "Ronald", Key.role.value: 'pusher',
                               Key.date.value: _current_time_()})
    dbManager.insert(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'})

    dbManager.insert(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '002'},
                     document={Key.id.value: "002", Key.nick.value: "Meta", Key.role.value: 'pusher',
                               Key.date.value: _current_time_()})

    dbManager.insert(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '003'},
                     document={Key.id.value: "003", Key.nick.value: "Raul", Key.role.value: 'puller',
                               Key.date.value: _current_time_()})

    dbManager.insert(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                     document=[{Key.id.value: "004", Key.nick.value: "Figo", Key.role.value: 'pusher',
                                Key.date.value: _current_time_()},
                               {Key.id.value: "005", Key.nick.value: "Messi", Key.role.value: 'puller',
                                Key.date.value: _current_time_()}])

    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))

    result = dbManager.count(vid_gid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    print("count: " + str(result))

    dbManager.update(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                     value='shanghai')

    print("update node")
    dbManager.update(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                     key=Key.location.value, value='shanghai')
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))
    print("update condition")
    dbManager.update(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                     condition={Key.role.value: 'puller'}, key='mm', value='puller')
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))
    print("update condition node")
    dbManager.update(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '002'},
                     condition={Key.location.value: "shanghai"}, key=Key.role.value, value='pusher')
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))
    result = dbManager.count(vid_gid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                             condition={Key.location.value: "shanghai"})
    print("condition count: " + str(result))

    print("remove: ")
    dbManager.remove(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                     condition={Key.id.value: "002"})
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))

    print("move: ")
    dbManager.move(vid_gid_src={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                   vid_gid_des={Key.vendor.value: 'VendorA', Key.group.value: 'GroupB'},
                   condition={Key.role.value: 'puller'})
    print("moved GroupA: ")
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'})
    for i in result:
        print(str(i))
    print("moved GroupB: ")
    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupB'})
    for i in result:
        print(str(i))

    result = dbManager.query(vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA'},
                             condition={Key.location.value: "shanghai"})
    print("query condition: ")
    for i in result:
        print(str(i))
    result = dbManager.query(
        vid_gid_nid={Key.vendor.value: 'VendorA', Key.group.value: 'GroupA', Key.node.value: '001'})
    print("query nodeID: ")
    for i in result:
        print(str(i))
    dbManager.close()
