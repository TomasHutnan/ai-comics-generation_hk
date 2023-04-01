# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import openai

DUMMY_STORY_DATA = {
    "characters": [{"name": "john",
                    "hair": "red",
                    "eyes": "green"}],
    "story": {
        "comic title": "John's intergalactic adventures",
        "story": "pilot john battles enemies in outer space",
        "style": "futuristic, digital art",
        "mood": "dark",
        "place": "space"
    }
}

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
        self.wfile.write(bytes(res_body, "utf-8"))
        #self.wfile.write(bytes(f'<img src="{res_body}" alt="GENERATED PHOTO" width="1024" height="1024">', "utf-8"))

    
    def handle_request(self, path: str, req_body: dict = {}) -> dict:
        split_path = path.strip("/").split("/")
        if split_path[0] == "image":
            print("req: "+split_path[-1])
            return self.image_prompt(split_path[-1])
        elif split_path[0] == "api":
            if split_path[1] == "story":
                return self.story(DUMMY_STORY_DATA)
        else:
            return self.bad_request()

    def bad_request(self):
        return {"body": "BAD_REQUEST"}

    def text_prompt(self, prompt: str) -> str:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        
        )
        return response.choices[0].text.strip()

    def story(self, data):
        character_string = ""

        for character in data["characters"]:
            for key in character:
                character_string += f"{key} - {character[key]}, "
            character_string += ";"

        story_string=""
        for key in data["story"]:
            story_string += f'{key} - {data["story"][key]}, '
        
        prompt_string = f"Summarize every panel of the story, describe every panel without context from the others, describe the characters instead of mentioning their names, describe the characters in each panel. take character apearence from this:{character_string} and here is the story: "+story_string

        print(prompt_string)

        return json.dumps(self.text_prompt(prompt_string), separators=(',', ':'))


    def image_prompt(self, prompt: str, size: int = 1024) -> str:
        guides = "digital art, clear lines, comic book, artwork, HD, color, 4K, warner brothers, DC comics, marvel, "
        response = openai.Image.create(
            prompt=(guides+prompt)[:400],
            n=1,
            size=f"{size}x{size}"
        )

        image_url = response['data'][0]['url']

        return f'<img src="{image_url}" alt="GENERATED PHOTO" width="1024" height="1024">'

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


