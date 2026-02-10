import os
import requests
import random
from vk_publisher import publish_post_to_vk


def get_image(url):
    if not url.startswith("http"):
        raise ValueError("Недопустимое URL изображения")
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filename = "comics.png"
    file_path = os.path.join(images_dir, filename)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def get_comics():
    choiced_comics = random.randint(1, 3205)
    url = f'https://xkcd.com/{choiced_comics}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    response_data = response.json()
    return response_data


def main():
    image_source = get_comics()['img']
    post_text = get_comics()['alt']
    published_comics = publish_post_to_vk(post_text, get_image(image_source))


if __name__ == '__main__':
    main()
