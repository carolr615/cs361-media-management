import zmq
import json
import os
import binascii
from uuid import uuid4

data_store = {"images": {}, "tags": {}, "texts": {}}

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:1000")

IMAGE_DIR = "stored_images"
TEXT_DIR = "stored_texts"
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

TEXT_WORD_LIMIT = 200

def validate_text(text):
    if not text.strip():
        return False, "Text cannot be empty."
    if len(text.split()) > TEXT_WORD_LIMIT:
        return False, f"Text exceeds {TEXT_WORD_LIMIT} words."
    return True, "Valid text."

def save_image(file_name, file_data, tags):
    try:
        # Convert hex-encoded image data back to bytes
        file_bytes = bytes.fromhex(file_data)
    except binascii.Error:
        return False, "Invalid image data format."
    
    file_path = os.path.join(IMAGE_DIR, file_name)
    with open(file_path, "wb") as file:
        file.write(file_bytes)
    
    data_store["images"][file_name] = file_path
    for tag in tags:
        if tag not in data_store["tags"]:
            data_store["tags"][tag] = []
        data_store["tags"][tag].append(file_name)
    
    return True, "Image uploaded successfully."

def save_text_file(title, text_content):
    file_name = f"{title}.txt"
    file_path = os.path.join(TEXT_DIR, file_name)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text_content)
    
    data_store["texts"][title] = file_path
    return file_path

def retrieve_image(file_name):
    if file_name in data_store["images"]:
        file_path = data_store["images"][file_name]
        with open(file_path, "rb") as file:
            return file.read().hex()
    return None

def retrieve_text(title):
    if title in data_store["texts"]:
        file_path = data_store["texts"][title]
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return None

def handle_request(request):
    action = request.get("action")
    
    if action == "upload_image":
        file_name = request.get("image_name")  # Fixed to match client key
        file_data = request.get("image_data")
        tags = request.get("tags", [])
        
        if not file_name or not file_data:
            return {"status": "error", "message": "Invalid image data."}
        
        success, message = save_image(file_name, file_data, tags)
        return {"status": "success" if success else "error", "message": message}
    
    elif action == "store_text":
        text = request.get("text", "")
        title = request.get("title", str(uuid4()))  # Ensure a unique ID if no title given
        valid, msg = validate_text(text)
        if not valid:
            return {"status": "error", "message": msg}
        file_path = save_text_file(title, text)
        return {"status": "success", "message": "Text saved.", "title": title, "file_path": file_path}
    
    elif action == "search_images":
        tag = request.get("tag")
        
        if tag in data_store["tags"]:
            image_list = data_store["tags"][tag]
            image_data = {file_name: retrieve_image(file_name) for file_name in image_list}
            return {"status": "success", "images": image_list, "image_data": image_data}
        else:
            return {"status": "error", "message": "No images found with this tag."}
    
    elif action == "get_image":
        file_name = request.get("image_name")  # Fixed to match client
        image_data = retrieve_image(file_name)
        if image_data:
            return {"status": "success", "image_name": file_name, "image_data": image_data}
        return {"status": "error", "message": "Image not found."}
    
    elif action == "get_text":
        title = request.get("title")  # Fixed key to match client
        text_content = retrieve_text(title)
        if text_content:
            return {"status": "success", "title": title, "text": text_content}
        return {"status": "error", "message": "Text file not found."}
    
    return {"status": "error", "message": "Unknown action."}

while True:
    message = socket.recv_string()
    request = json.loads(message)
    response = handle_request(request)
    socket.send_string(json.dumps(response))
