from flask import Flask, jsonify, request
import requests
import openai
import json

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
    data = requests.post('http://localhost:5000/api/users', data=jsonify({"test": "TEST_DATA"}))

    return data

@app.route('/image', methods=['GET'])
def image_completion():
    return image_prompt(str(request.query_string))

@app.route('/api/story', methods=['GET'])
def story_completion():
    return story(DUMMY_STORY_DATA)

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

def story(data):
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


def image_prompt(prompt: str, size: int = 1024) -> str:
    guides = "digital art, clear lines, comic book, artwork, HD, color, 4K, "
    response = openai.Image.create(
        prompt=(guides+prompt)[:400],
        n=1,
        size=f"{size}x{size}"
    )

    image_url = response['data'][0]['url']

    return f'<img src="{image_url}" alt="GENERATED PHOTO" width="1024" height="1024">'


if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True)