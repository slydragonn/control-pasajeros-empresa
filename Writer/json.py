import json

def create_json_file(Dic):
    json_string = json.dumps(Dic, indent=4)
    json_file = open("./Output/result.json", "w")
    json_file.write(json_string)
    json_file.close()