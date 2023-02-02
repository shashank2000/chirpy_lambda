import json

# Open the file for reading
with open('request', 'r') as file:
    # Read the contents of the file
    file_contents = file.read()

# Convert the contents of the file to a JSON object
json_object = json.loads(file_contents)

from app import handler
print(handler(json_object, None))