from flask import Flask, jsonify, request
import requests
import openai
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont
import io, base64

FONT_FILE = "../Comic_Book.otf"
openai.api_key_path="../openai_key.txt"

app = Flask(__name__)

####### TEST
""" @app.route('/test', methods=['GET'])
def test_picture():
    response = requests.post("http://127.0.0.1:5000/api/character/picture", json={"character":{
        "name": "Tom",
        "attributes": ["A"],
        "skin": "A",
        "hair": ["A"],
        "physical": ["A"],
        "clothes": ["A"],
    }})

    return response.content """

####### TEST

@app.route('/api/story/generate', methods=['POST']) # mas formular - return vygenerovany story
def generate_story():
    data = request.get_json()

    context = ". ".join([data["mood"], data["location"], data["style"]])
    story = story_completion(context, data["name"])

    characters = parse_character_form(data["characters"], story)

    complete_story = continue_story(story, characters)

    return complete_story

@app.route('/api/story/continue', methods=['POST']) # mas story a characterov - return vygenerovany story
def continue_generated_story():
    data = request.get_json()

    story = data["story"]
    characters = parse_character_form(data["characters"], story)

    story_continuation = continue_story(story, characters)

    return story_continuation

@app.route('/api/panel/descriptions', methods=['POST']) # mas story a characterov - return descriptiony
def generate_panel_descriptions():
    data = request.get_json()

    story = data["story"]
    characters = parse_character_form(data["characters"], story)

    descriptions = get_image_descriptions(story, characters)

    return jsonify(descriptions)

@app.route('/api/panel/generate', methods=['POST']) # mas descr + prompt - return b64 panel {"prompt": "","caption": ""}
def generate_panel():
    data = request.get_json()

    image_url = image_prompt(data["prompt"])
    b64 = str(base64.b64encode(requests.get(image_url).content), encoding="utf-8")
    captioned_b64 = draw_caption(b64, data["caption"][:200])

    return str(captioned_b64)

@app.route('/api/character/picture', methods=['POST']) # mas charactera - return b64 picture
def generate_character_picture():
    data = request.get_json()
    
    #character = parse_character_form([data["character"]], "")

    char_prompt = make_character_image(data["character"])
    image_url = image_prompt(char_prompt, 256)
    b64 = str(base64.b64encode(requests.get(image_url).content), encoding="utf-8")

    return b64


###################

def parse_character_form(form, story):
    characters = {}
    for char in form:
        prompt = ""

        if char["attributes"]:
            prompt += "Their attributes are " + ", ".join(char["attributes"]) + ". "
        if char["skin"]:
            prompt += "Their skin is " + char["skin"] + ". "
        if char["hair"]:
            prompt += "Their hair is " + ", ".join(char["hair"]) + ". "
        if char["physical"]:
            prompt += "They are " + ", ".join(char["physical"]) + ". "
        if char["clothes"]:
            prompt += "Their clothes are " + ", ".join(char["clothes"]) + ". "
        
        character = character_completion(char["name"], story, prompt)

        characters[char["name"]] = character
    
    return characters

###################

def story_completion(context , prompt):
    info = openai.Completion.create(
        engine="text-davinci-003",
        prompt="I want you to ACT like the best story teller. Finish this story:"+ context + prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    

    message = info.choices[0].text.strip()
    return message
   

def character_completion(name,context,prompt):
    root = f"Make {name} a more interesting character, keep in mind that the plot doesn't allow {name} to die at this point in the story. Describe their appearance ONLY using keywords separated by commas. The description mainly consists of visual aspects, such as clothing, gadgets, etc."
    info = openai.Completion.create(
        engine="text-davinci-003",
        prompt=root,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=root + context +":" + prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    
    )

    message = response.choices[0].text.strip()

    return name,message


def character_creation(story,existing_characters):
    existing_characters_string = Strigify_Characters(existing_characters)
    
    root = f"Try to create a single character that is not yet mentioned here:{existing_characters_string},describe his apearence in 10 keywords. Make sure the character will fit well into this story :" + story 
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=root ,
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    message = response.choices[0].text.strip()
    print(message)
    name = openai.Completion.create(
        engine="text-davinci-003",
        prompt= f"what is the name of this described character:{message}if her character name is not mention make one that would fit the description. Your answer will be just the name nothing else." ,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    name_string = name.choices[0].text.strip()

    return name_string,message


def continue_story(story,characters):
    characters = Strigify_Characters(characters)
    context = f"You are an experienced story teller. Now make a long continuation with these characters:{characters} for this story:{story}. Be awere that the end of this story is still very far."
    become = openai.Completion.create(
        engine="text-davinci-003",
        prompt=context ,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    


    message = become.choices[0].text.strip()
    return message
def Strigify_Characters(character_dict):
    string = ""
    for i in character_dict.keys():
        string += "\n"+i +":"+"\n"+"".join(character_dict[i])
    return string


def dict_to_json(my_dict):
   
    json_data = json.dumps(my_dict)

    return json_data


def get_image_descriptions(story,character):
    character_string = Strigify_Characters(character)
    apearence = openai.Completion.create(
        engine="text-davinci-003",
        prompt = f"The characters in the story look acordingly: {character_string}",
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    
    )

    keywords = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"ACT like a comic book writer. Remake the following story into at least 12 comic panels. Every panel has to have a visual description in the form of keywords separated by commas of the environment i.e.: Environment name(brief description of the environment). When describing characters and environments ALWAYS treat EVERY SINGLE panel as STANDALONE and be VERY SPECIFIC. For the descriptions use the following format: Character Name(brief descritption of the characters visual with keywords separated by commas, consisting of CLOTHING, gadgets, etc.). So your output for every specific will look like this: 'Evironment Name(description as before), Action(part of story for specific panel), Character(description as before)'. Here's the story: {story} ",
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.1,
    
    )
    keywords_string = keywords.choices[0].text.strip()
    story_telling = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Act as a narrator. You are going to narate comic book story that is separated into 12 panels. Provide a separate naration for every panel. Narrate this story:{story} Keep it in range of 30 50 words for each panel.",
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    naration = story_telling.choices[0].text.strip()
    print(naration)
    list = []
    for i in range(12):
        list.append({})
        list[i]["prompt"] = keywords_string.split("Panel")[i+1].split(":")[1]
        list[i]["caption"] = naration.split("Panel")[i+1].split(":")[1]
    print(list)
    return list

def make_character_image(character_dict):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f'You are Assistent of a blind painter and you need to describe him his paint subjects apearance in a very detailed manner. The paints subjects traits are:Skin tone:{character_dict["skin"]},hair:{",".join(character_dict["hair"])}, physical apearence:{",".join(character_dict["physical"])},clothes:{",".join(character_dict["clothes"])}.',
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    message = response.choices[0].text.strip()
    return message

######################

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

######################

def draw_caption(img="test.png", caption="Flash Gordon and his team of superhumans are travelling through the universe, fighting off hordes of aliens and robots."):
    wrapper = textwrap.TextWrapper(width=43, max_lines=5)
    word_list = wrapper.wrap(text=caption) 
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]

    image = Image.open(io.BytesIO(base64.b64decode(img)))
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_FILE, size=36)
    w,h = draw.textsize(caption_new, font)
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


if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True)