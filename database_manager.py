from flask import jsonify
import sqlite3 as sql
from jsonschema import validate
from flask import current_app

schema = {
      "type": "object",
      "validationLevel": "strict",
      "required": [
            "name",
            "hyperlink",
            "about",
            "image",
            "language",
      ],
      "properties": {
            "name": {"type": "string"},
            "hyperlink": {
                  "type": "string",
                  "pattern": r"^https:\/\/marketplace\.visualstudio\.com\/items\?itemName=(?!.*[<>])[a-zA-Z0-9\-._~:\/?#\[\]@!$&'()*+,;=]*$",
            },
            "about": {"type": "string"},
            "image": {
                  "type": "string",
                  "pattern": r"^https:\/\/(?!.*[<>])[a-zA-Z0-9\-._~:\/?#\[\]@!$&'()*+,;=]*$",
            },
            "language": {
                  "type": "string",
                  "enum": ["PYTHON", "CPP", "BASH", "SQL", "HTML", "CSS", "JAVASCRIPT"],
            },
      },
      "additionalProperties": False,
}

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

def validate_json(json_data):
      try:
            validate(instance=json_data, schema=schema)
            return True
      except:
            return False

def extension_add(data):
      if validate_json(data):
            with sql.connect("database/data_source.db") as con:
                  cur = con.cursor()
                  cur.execute(
                        "INSERT INTO extension (name, hyperlink, about, image, language) VALUES (?, ?, ?, ?, ?)",
                        [
                              data["name"],
                              data["hyperlink"],
                              data["about"],
                              data["image"],
                              data["language"],
                        ],
                  )
                  con.commit()
            return jsonify({"message": "Extension added successfully"}), 201
      else:
            return jsonify({"error": "Invalid JSON"}), 400
      
