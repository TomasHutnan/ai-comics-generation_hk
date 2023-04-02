from PIL import Image, ImageDraw, ImageFont
import openai
import io
import base64
import textwrap
import requests
import time

FONT_FILE = "Comic_Book.otf"
openai.api_key_path="openai_key.txt"

def generate_panel(prompt, caption):
    image_url = image_prompt(prompt)
    b64 = str(base64.b64encode(requests.get(image_url).content), encoding="utf-8")
    captioned_b64 = draw_caption(b64, caption[:200])

    return captioned_b64

def image_prompt(prompt: str, size: int = 1024) -> str:
    guides = "digital art, clear lines, comic book, artwork, HD, color, 4K, story, "
    response = openai.Image.create(
        prompt=(guides+prompt)[:400],
        n=1,
        size=f"{size}x{size}"
    )
    image_url = response['data'][0]['url']

    return image_url

def draw_caption(img="test.png", caption="Flash Gordon and his team of superhumans are travelling through the universe, fighting off hordes of aliens and robots."):
    wrapper = textwrap.TextWrapper(width=50) 
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

def generate_panels(data):
    panels = []
    for i in range(len(data)):
        panel = str(generate_panel(data[i]["description"], data[i]["naration"]), "utf-8")
        panels.append(panel)

    for round in range(2):
        dst = Image.new('RGB', (1024*2, 1024*3))
        for y in range(3):
            for x in range(2):
                im = Image.open(io.BytesIO(base64.b64decode(panels[round*6 + y*2 + x])))
                dst.paste(im, (x*1024, y*1024))
        dst.save(f"COMIC-{time.gmtime()}.png")

generate_panels([{'description': ' Street(dark alleyway, cobblestone pavement, street lamps), Marco walking towards the mafia hideout. Marco(black leather jacket, jeans, sneakers, determined expression). \n\n', 'naration': ' The world was dangerous and dark, full of secrets and violence. People lived in constant danger of getting caught up in the wrong kind of trouble.\n\n'}, {'description': ' Inside the mafia hideout(dimly lit room, wooden tables, chairs, people talking in hushed tones). Marco(same as before, looking around nervously). \n\n', 'naration': ' Marco decided to take a chance and join the mafia, hoping to experience wealth and power.\n\n'}, {'description': ' Rival mafia boss(black suit, menacing expression) confronting Marco. \n\n', 'naration': ' But Marco quickly found out that life in the mafia was not what he had expected. He was in danger and had to make life-or-death decisions.\n\n'}, {'description': ' Marco(fearful expression, sweating) trying to explain his situation to the mafia boss. \n\n', 'naration': ' One day, Marco was confronted by a rival mafia boss who demanded money or else Marco would be killed.\n\n'}, {'description': ' Mysterious stranger(black trench coat, hat, sunglasses) stepping in and offering to help Marco. \n\n', 'naration': ' A mysterious stranger stepped in and offered to help Marco, providing the money in exchange for Marco working for him.\n\n'}, {'description': ' Marco(surprised expression) looking at the stranger in disbelief. \n\n', 'naration': ' Marco reluctantly agreed and the stranger gave him the money. He also said Marco could make a new life for himself if he was willing to take it.\n\n'}, {'description': " Marco(resigned expression) reluctantly agreeing to the stranger's offer. \n\n", 'naration': ' Marco was now working for the mysterious stranger and slowly learning the ropes of the mafia.\n\n'}, {'description': ' Marco(determined expression) working for the mysterious stranger and learning the ropes of the mafia. \n\n', 'naration': ' He was becoming more powerful and respected in the mafia, making a name for himself.\n\n'}, {'description': ' Marco(confident expression) becoming more powerful and respected in the mafia. \n\n', 'naration': ' But Marco was still haunted by his past. He was determined to repay the debt he owed the mysterious stranger.\n\n'}, {'description': ' Marco(determined expression) determined to repay the debt to the mysterious stranger. \n\n', 'naration': ' After years of hard work, Marco was able to pay off the debt and become a respected member of the mafia.\n\n'}, {'description': ' Marco(smiling expression) paying off the debt and becoming a respected member of the mafia. \n\n', 'naration': ' He had achieved his dream of becoming a powerful and respected figure in the mafia, no longer living in fear.\n\n'}, {'description': ' Marco(smiling expression) realizing that life in the mafia is dangerous but full of opportunities.', 'naration': ' Marco had learned a valuable lesson'}])
