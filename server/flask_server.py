from flask import Flask, jsonify, request
import requests
import openai
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont
import io, base64

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

FONT_FILE = "../Comic_Book.otf"
openai.api_key_path="../openai_key.txt"

app = Flask(__name__)

# Define a route to handle GET requests to the /api/users endpoint
@app.route('/api/users', methods=['POST'])
def get_users():
    data = request.get_json()
    print(data["test"])
    # Query a database or perform some other data processing
    users = [
        {'id': 1, 'name': 'John'},
        {'id': 2, 'name': 'Jane'}
    ]
    # Convert the data to a JSON format and return it in the response
    return jsonify(users)

@app.route('/api/test', methods=['GET'])
def test_users():
    data = requests.post('http://localhost:5000/api/panel', json={"prompt": "City Street(dark alleyway, street lamps, graffiti on walls), Action(man in a suit walking down the street, looking around suspiciously), Character(man in a suit, black hat, sunglasses, briefcase). ", "caption": "Life was a hard one for many. It was a life of crime, violence, and corruption."})

    return get_html_image(data.content)

@app.route('/image', methods=['GET'])
def image_completion():
    query = str(request.query_string)
    image_url = image_prompt(query)
    b64 = str(base64.b64encode(requests.get(image_url).content), encoding="utf-8")
    captioned_b64 = draw_caption(b64, query.replace("%20", " ")[:200])

    return get_html_image(captioned_b64)

@app.route('/api/panel', methods=['POST'])
def api_panel():
    data = request.get_json()

    image_url = image_prompt(data["prompt"])
    b64 = str(base64.b64encode(requests.get(image_url).content), encoding="utf-8")
    captioned_b64 = draw_caption(b64, data["caption"][:200])

    return captioned_b64


@app.route('/api/story', methods=['POST'])
def story_completion():
    data = request.get_json()
    
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

    return text_prompt(prompt_string)

###################
def text_prompt(prompt: str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    return response.choices[0].text.strip()

def image_prompt(prompt: str, size: int = 1024) -> str:
    guides = "digital art, clear lines, comic book, artwork, HD, color, 4K, story, "
    response = openai.Image.create(
        prompt=(guides+prompt)[:400],
        n=1,
        size=f"{size}x{size}"
    )
    image_url = response['data'][0]['url']

    return image_url
######################3

def get_html_image(image_url):
    return f'<img src="data:image/png;base64, {str(image_url, encoding="utf-8")}" alt="GENERATED PHOTO" width="1024" height="1024">'

def draw_caption(img="test.png", caption="Flash Gordon and his team of superhumans are travelling through the universe, fighting off hordes of aliens and robots."):
    wrapper = textwrap.TextWrapper(width=50) 
    word_list = wrapper.wrap(text=caption) 
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]

    image = Image.open(io.BytesIO(base64.b64decode(img)))
    draw = ImageDraw.Draw(image)

    # Download the Font and Replace the font with the font file. 
    font = ImageFont.truetype(FONT_FILE, size=36)
    w,h = draw.textsize(caption_new, font)#, font=font)
    #print(w, h)
    W,H = image.size
    x,y = 0.5*(W-w),0.90*H-h
    draw.rectangle((x-20, y, 1024-x+20, 1024-75), fill="black")
    draw.text((x, y), caption_new, font=font)
    
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format = "PNG")
    # reset file pointer to start
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()

    base64_encoded_result_bytes = base64.b64encode(img_bytes)
    #base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
    return base64_encoded_result_bytes


####
####
####
if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True)