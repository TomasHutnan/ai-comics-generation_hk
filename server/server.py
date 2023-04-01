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
        self.send_header("Content-type", "application/json")
        self.end_headers()

        print("HERE")
        #print(self.path.strip("/").split("/")[1])
        res_body = self.handle_request(self.path)
        self.wfile.write(bytes(json.dumps(res_body, separators=(',', ':'))))

    
    def handle_request(self, path: str, req_body: dict = {}) -> dict:
        if path.strip("/").split("/")[0] == "image":
            return self.image_prompt(path[-1])
        else:
            return self.bad_request()

    def bad_request(self):
        return {"body": "BAD_REQUEST"}

    def text_prompt(self, prompt: str) -> str:
        pass

    def image_prompt(self, prompt: str, size: int = 256) -> str:
        response = openai.Image.create(
            prompt=prompt,
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


