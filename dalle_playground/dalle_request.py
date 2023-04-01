import openai
import urllib.request
import sys # to access the system
import cv2

###########
prompt = "Retro-futuristic art style, adventurous mood, dangerous and exciting atmosphere, diverse and visually stunning environment, classic and timeless feel, emphasis on heroism, action, and the triumph of good over evil, image, print, painting, graphic, no text, without text. We see Flash Gordon and his companions, including the brave pilot Dale Arden and the eccentric scientist Dr. Hans Zarkov, flying in a sleek spaceship towards the planet Mongo."
###########

openai.api_key = "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"

def generate_dalle_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256"
    )

    image_url = response['data'][0]['url']

    return image_url

image_url = generate_dalle_image(prompt)
# print(image_url)

file_name = "dalle_result.png"
urllib.request.urlretrieve(image_url, file_name)

img = cv2.imread(file_name, cv2.IMREAD_ANYCOLOR)
 
while True:
    cv2.imshow(file_name, img)
    cv2.waitKey(0)
    sys.exit() # to exit from all the processes
 
cv2.destroyAllWindows() # destroy all windows