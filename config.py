from utils.database import DataBase


__tables__ = [{
        'name': 'global',
        'attr': [{
                'key': 'name',
                'db_type': 'TEXT UNIQUE NOT NULL',
            }, {
                'key': 'value',
                'db_type': 'BLOB',
            }, {
                'key': 'valid',
                'db_type': 'FLOAT',
            }
        ]
    }, {
        'name': 'code',
        'attr': [{
                'key': 'id',
                'db_type': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            }, {
                'key': 'code',
                'db_type': 'TEXT NOT NULL'
            }, {
                'key': 'valid',
                'db_type': 'FLOAT'
            },
        ],
    }, {
        'name': 'user',
        'attr': [{
                'key': 'id',
                'db_type': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            }, {
                'key': 'username',
                'db_type': 'TEXT UNIQUE NOT NULL',
            }, {
                'key': 'password',
                'db_type': 'TEXT NOT NULL',
            }, {
                'key': 'code',
                'db_type': 'TEXT',
            }, {
                'key': 'level',
                'db_type': 'INTEGER',
            }
        ], 'extra': [
            'FOREIGN KEY (code) REFERENCES code(code)',
        ]
    }, {
        'name': 'log',
        'attr': [{
                'key': 'id',
                'db_type': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            }, {
                'key': 'content',
                'db_type': 'TEXT',
            }, {
                'key': 'user_id',
                'db_type': 'INTEGER',
            }, {
                'key': 'time',
                'db_type': 'FLOAT',
            },
        ], 'extra': [
            'FOREIGN KEY (user_id) REFERENCES user(id)',
        ],
    },  {
        'name': 'dashboard',
        'attr': [{
                'key': 'id',
                'db_type': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            }, {
                'key': 'data',
                'db_type': 'BLOB',
            }, {
                'key': 'time',
                'db_type': 'FLOAT',
            },
        ]
    },
]


if __name__ == '__main__':
    pass

db = DataBase('data.db', tables=__tables__)
