# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import openai

hostName = "localhost"
serverPort = 8080

openai.api_key_path="../openai_key.txt"

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        #self.send_header("Content-type", "application/json")
        self.send_header("Content-type", "text/html")
        self.end_headers()

        print("HERE")
        #print(self.path.strip("/").split("/")[1])
        res_body = self.handle_request(self.path)
        #self.wfile.write(bytes(json.dumps(res_body, separators=(',', ':')), "utf-8"))
        self.wfile.write(bytes(f'<img src="{res_body}" alt="GENERATED PHOTO" width="1024" height="1024">', "utf-8"))

    
    def handle_request(self, path: str, req_body: dict = {}) -> dict:
        split_path = path.strip("/").split("/")
        if split_path[0] == "image":
            print("req: "+split_path[-1])
            return self.image_prompt(split_path[-1])
        elif split_path[0] == "api":
            if split_path[1] == "story":
                pass
        else:
            return self.bad_request()

    def bad_request(self):
        return {"body": "BAD_REQUEST"}

    def text_prompt(self, prompt: str) -> str:
        openai.ChatCompletion.create(
            prompt=prompt,
            n=1,
        )
        pass

    def image_prompt(self, prompt: str, size: int = 1024) -> str:
        guides = "image, digital art, clear lines; "
        response = openai.Image.create(
            prompt=(guides+prompt)[:400],
            n=1,
            size=f"{size}x{size}"
        )

        image_url = response['data'][0]['url']

        return image_url

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


