
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query

import tinydb_orm as models

db_file = tempfile.NamedTemporaryFile(suffix='.json')
db = TinyDB(db_file.name)


class User(models.Model):
    name = models.Str()
    password = models.Str(default='')

    class Meta:
        db = db
        table_name = 'user'
        unique_together = ['name']
