import openai
import urllib.request
import sys # to access the system
import cv2

###########
prompt = input("Prompt: ")
###########

openai.api_key_path="../openai_key.txt"

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