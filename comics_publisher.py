import os
import requests
import random
from environs import Env
from vk_publisher import VK_API_VERSION, publish_post_to_vk

NUMBER_OF_COMICS = 3205

def get_image(url, images_dir='images'):
    if not url.startswith('http'):
        raise ValueError('Недопустимое URL изображения')
    response = requests.get(url)
    response.raise_for_status()
    filename = 'comic.png'
    file_path = os.path.join(images_dir, filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def get_random_comic(NUMBER_OF_COMICS):
    choiced_comic = random.randint(1, NUMBER_OF_COMICS)
    url = f'https://xkcd.com/{choiced_comic}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    xkcd_response = response.json()
    return xkcd_response


def main():
    try:
        comic = get_random_comic(NUMBER_OF_COMICS)
        image_source = comic['img']
        post_text = comic['alt']
        images_dir = 'images'
        os.makedirs(images_dir, exist_ok=True)

        env = Env()
        env.read_env()
        vk_api_token = env.str('VK_API_TOKEN')
        vk_group_id = env.int('VK_GROUP_ID')

        published_comics = publish_post_to_vk(
            post_text,
            get_image(image_source, images_dir),
            vk_group_id,
            vk_api_token,
            VK_API_VERSION,
        )
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'Сетевой запрос не удался: {e}') from e
    except (KeyError, ValueError) as e:
        raise RuntimeError(f'Недействительный ответ API: {e}') from e


if __name__ == '__main__':
    main()
