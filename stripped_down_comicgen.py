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
        dst.save(f"COMIC-{str(round(time.time()))}.png")

generate_panels([{'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Marco walking, Marco(black leather jacket, jeans, sneakers, determined expression). \n\n', 'naration': ' The world was a dangerous and dark place, full of secrets and violence. People were constantly in danger of getting caught up in the wrong kind of trouble. \n\n'}, {'description': ' Inside a Bar(dimly lit, smokey, people talking in hushed tones), Marco talking to a mafia boss, Mafia Boss(black suit, white shirt, black tie, menacing expression). \n\n', 'naration': ' Marco decided to take a chance and join the mafia. He wanted to experience the wealth and power he had heard stories about. \n\n'}, {'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Marco looking scared, Marco(black leather jacket, jeans, sneakers, terrified expression). \n\n', 'naration': ' Marco quickly found out that life in the mafia was not what he expected. He was constantly in danger and had to make decisions that could mean life or death. \n\n'}, {'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Mysterious Stranger stepping in, Mysterious Stranger(black trench coat, black fedora, sunglasses, calm expression). \n\n', 'naration': ' One day, Marco was confronted by a rival mafia boss who demanded money or else he would be killed. Marco had no way of paying. \n\n'}, {'description': ' Inside a Bar(dimly lit, smokey, people talking in hushed tones), Marco and Mysterious Stranger talking, Marco(black leather jacket, jeans, sneakers, determined expression), Mysterious Stranger(black trench coat, black fedora, sunglasses, calm expression). \n\n', 'naration': " Just then, a mysterious stranger stepped in and offered to help Marco. He said he would provide the money in exchange for Marco's service. \n\n"}, {'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Marco walking away, Marco(black leather jacket, jeans, sneakers, determined expression). \n\n', 'naration': ' Marco reluctantly agreed and the stranger gave him the money. He also offered Marco a chance to make a new life for himself. \n\n'}, {'description': ' Inside a Warehouse(dark, dusty, crates and boxes scattered around), Marco talking to a group of mafia members, Marco(black leather jacket, jeans, sneakers, determined expression), Mafia Members(black suits, white shirts, black ties, menacing expressions). \n\n', 'naration': ' Marco was working for the mysterious stranger, becoming more powerful and respected in the mafia. \n\n'}, {'description': ' Inside a Warehouse(dark, dusty, crates and boxes scattered around), Marco and Mafia Members talking, Marco(black leather jacket, jeans, sneakers, determined expression), Mafia Members(black suits, white shirts, black ties, menacing expressions). \n\n', 'naration': ' But Marco was still haunted by his past and was determined to repay the debt he owed to the stranger. \n\n'}, {'description': ' Inside a Bar(dimly lit, smokey, people talking in hushed tones), Marco paying off the mafia boss, Marco(black leather jacket, jeans, sneakers, relieved expression), Mafia Boss(black suit, white shirt, black tie, menacing expression). \n\n', 'naration': ' After years of hard work, Marco was able to pay off the debt and become a respected member of the mafia. \n\n'}, {'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Marco walking away, Marco(black leather jacket, jeans, sneakers, determined expression). \n\n', 'naration': ' Marco had achieved his dream and was no longer living in fear. He had learned a valuable lesson. \n\n'}, {'description': ' Inside a Bar(dimly lit, smokey, people talking in hushed tones), Marco talking to a group of mafia members, Marco(black leather jacket, jeans, sneakers, confident expression), Mafia Members(black suits, white shirts, black ties, respectful expressions). \n\n', 'naration': ' Life in the mafia is dangerous and unpredictable, but it is also full of opportunities if you have the courage to take them. \n\n'}, {'description': ' City Street(dark alleyway, street lamps, graffiti on walls), Marco walking away, Marco(black leather jacket, jeans, sneakers, confident expression).', 'naration': ' Marco had taken the chance and it had paid off. He was now a respected figure in the mafia.'}])
