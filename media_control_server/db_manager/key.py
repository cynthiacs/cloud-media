from enum import Enum, unique


@unique
class Key(Enum):
    """
    database key:
    db         ----> vendor
    collection ----> group
    """
    vendor = 'vendor'
    group = 'group'
    default_group = 'default'
    node = 'node'
    """
    document key:
    """
    id = 'id'
    nick = 'nick'
    role = 'role'
    location = 'location'
    stream_status = 'stream_status'
    vendor_id = 'vendor_id'
    vendor_nick = 'vendor_nick'
    group_id = 'group_id'
    group_nick = 'group_nick'
    date = 'date'
    nRef = 'nRef'
