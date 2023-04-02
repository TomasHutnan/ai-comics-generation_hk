import openai
import json
openai.api_key = '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'

Characters = {}

def story_completion(context , prompt):
    root = "Finish this first opening chapter of story:"
    info = openai.Completion.create(
        engine="text-davinci-003",
        prompt="I want you to ACT like the best story teller. Finish this story:"+ context + prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    
    )
    

    message = info.choices[0].text.strip()
    with open("story.txt", "w") as file:
       file.write(message)
   

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
        string += "\n"+i +":"+"\n"+character_dict[i]
    return string


def dict_to_json(my_dict):
   
    json_data = json.dumps(my_dict)

    return json_data
def make_keywords(story,character):
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
        list[i]["description"] = keywords_string.split("Panel")[i+1].split(":")[1]
        list[i]["naration"] = naration.split("Panel")[i+1].split(":")[1]
    print(list)
    return keywords_string


story_root = "The end Italian mafia"

story_conext = "A sad and critical story regarding life in mafia"
mc_name = "Lukas"
story_completion(story_conext,story_root)


with open('story.txt', 'r') as file:
    story = file.read()

character = character_completion("Antonio",story_conext,"Main character of the story")
Characters[character[0]] = character[1]
character = character_creation(story,Characters)
Characters[character[0]] = character[1]
character = character_creation(story,Characters)
Characters[character[0]] = character[1]

with open("character.txt", "w") as file:
    file.write(dict_to_json(Characters))


next_story = continue_story(story,Characters)
with open("nextstory.txt", "w") as file:
    file.write(next_story)

print(make_keywords(story,Characters))



