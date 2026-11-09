from flask import jsonify
import sqlite3 as sql
from jsonschema import validate
from flask import current_app


def extension_get(lang):
      with sql.connect("database/data_source.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM extension WHERE language LIKE ?;", [lang])
            if lang.isalpha():
                  migrate_data = [
                        dict(
                              extID=row[0],
                              name=row[1],
                              hyperlink=row[2],
                              about=row[3],
                              image=row[4],
                              language=row[5],
                        )
                        for row in cur.fetchall()
                  ]
            else:
                  return jsonify("%")
      return jsonify(migrate_data)