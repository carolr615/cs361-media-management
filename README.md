# Media management microservice
This microservice allows users to upload and retrieve text, text files, as well as images. Both the client and the server must also be connected to the same socket or local host server to be able to interact with each other as well. Currently, the microservice is available at: tcp://localhost:1000

This microservice should be able to process: 
1. Text entered
2. A .txt file
3. Images

## Requesting Data
This microservice uses ZeroMQ REQ/REP pattern, where the client sends a request while the server retrieves and handles the logic. First, you need to set-up a function in your client function that looks something like this, which can then communicate with the main service: 

```
def send_request(request):
    socket.send_string(json.dumps(request))
    response_json = socket.recv_string()
    return json.loads(response_json)
```

Furthermore, you may also need to have another initilaizing function which handles the information that will be stored in a request, as well as where the information will be stored. For example, in the client-side code it also creates new directories to save images or files that may have been uploaded by the user. 

```
def upload_text_file():
    file_path = input("Enter the path of the text file to upload: ")
    
    if not os.path.exists(file_path):
        print("File does not exist.")
        return
    
    title = os.path.basename(file_path).rsplit(".", 1)[0] 
    
    with open(file_path, "r", encoding="utf-8") as file:
        text_content = file.read()
    
    request = {
        "action": "store_text",
        "title": title,
        "text": text_content
    }
    
    response = send_request(request)
    print("Response:", response)
```
## Receiving Data
Depending on how you configure your client side, the response can be simply printed: 
```
Response: {'status': 'success', 'title': 'basketball', 'text': 'Basketball is a sport'}
```

You can also retrieve and display uploaded images by importing something like the python PIL library. For example, here is a snippet in the example client where the image is searched for by the tag, and then displayed: 
```
for image_name, image_hex in response["image_data"].items():
            image_path = os.path.join("stored_images", image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(bytes.fromhex(image_hex))
            print(f"Image saved to {image_path}")
            
            img = Image.open(image_path)
            img.show()
```
This code also prints where the path where the image has been saved locally. 

## UML Diagram
![umldiagram](https://github.com/user-attachments/assets/29a7de93-81b2-4667-8820-280e39b6feae)

## Running the Microservice
This microservice requires ZeroMQ to be installed in order to run: 
``` pip install pyzmq ```

Finally, simply running the server and then the client should then enable the microservice to be able to interact with the client server. 

This microservice does not rely on my example test client in order to run. 
