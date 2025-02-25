import zmq
import json
import os
from PIL import Image

def send_request(request):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:1000")
    
    socket.send_string(json.dumps(request))
    response_json = socket.recv_string()
    return json.loads(response_json)

def upload_image():
    image_path = input("Enter the path of the image to upload: ")
    if not os.path.exists(image_path):
        print("File does not exist.")
        return
    
    image_name = os.path.basename(image_path)
    tags = input("Enter tags (comma-separated): ").split(',')
    
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    
    request = {
        "action": "upload_image",
        "image_name": image_name,
        "tags": [tag.strip() for tag in tags],
        "image_data": image_data.hex()
    }
    
    response = send_request(request)
    print("Response:", response)

def search_images():
    tag = input("Enter tag to search: ")
    request = {"action": "search_images", "tag": tag}
    response = send_request(request)

    if response["status"] == "success" and response["images"]:
        os.makedirs("stored_images", exist_ok=True)
        
        for image_name, image_hex in response["image_data"].items():
            image_path = os.path.join("stored_images", image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(bytes.fromhex(image_hex))
            print(f"Image saved to {image_path}")
            
            img = Image.open(image_path)
            img.show()
    else:
        print("No images found with that tag.")

def upload_text_file():
    file_path = input("Enter the path of the text file to upload: ")
    
    if not os.path.exists(file_path):
        print("File does not exist.")
        return
    
    title = os.path.basename(file_path).rsplit(".", 1)[0]  # Extract filename without extension
    
    with open(file_path, "r", encoding="utf-8") as file:
        text_content = file.read()
    
    request = {
        "action": "store_text",
        "title": title,
        "text": text_content
    }
    
    response = send_request(request)
    print("Response:", response)

if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1. Store Text")
        print("2. Get Text")
        print("3. Upload Text File") 
        print("4. Upload Image")
        print("5. Search Images by Tag")
        print("6. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            title = input("Enter title (or leave blank for auto ID): ")
            text = input("Enter text: ")
            request = {"action": "store_text", "title": title, "text": text}
        elif choice == "2":
            title = input("Enter title: ")
            request = {"action": "get_text", "title": title}
        elif choice == "3":  
            upload_text_file()
            continue
        elif choice == "4":
            upload_image()
            continue
        elif choice == "5":
            search_images()
            continue
        elif choice == "6":
            break
        else:
            print("Invalid choice, try again.")
            continue
        
        response = send_request(request)
        print("Response:", response)
