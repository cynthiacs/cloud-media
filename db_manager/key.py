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
    date = 'date'
    nRef = 'nRef'
