import requests
from environs import Env

env = Env()
env.read_env()

VK_API_TOKEN = env.str('VK_API_TOKEN')
VK_GROUP_ID = int(env.str('VK_GROUP_ID'))
VK_API_VERSION = '5.199'


def vk_call(method, params):
    url = f'https://api.vk.com/method/{method}'
    params = {
        **params,
        'access_token': VK_API_TOKEN,
        'v': VK_API_VERSION
    }
    try:
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'VK request failed: {e}') from e
    return response_data.get('response')


def upload_photo_for_wall(image_source):
    response = vk_call('photos.getWallUploadServer', {'group_id': VK_GROUP_ID})
    upload_url = response['upload_url']
    try:
        with open(image_source, 'rb') as file:
            files = {'photo': file}
            response = requests.post(upload_url, files=files, timeout=30)
            response.raise_for_status()
            upload_response = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'VK request failed: {e}') from e
    except ValueError as e:
        raise ValueError(f'VK returned invalid JSON: {e}') from e
    saved = vk_call(
        'photos.saveWallPhoto',
        {
            'group_id': VK_GROUP_ID,
            'photo': upload_response['photo'],
            'server': upload_response['server'],
            'hash': upload_response['hash'],
        },
    )
    photo = saved[0]
    return f"photo{photo['owner_id']}_{photo['id']}"


def publish_post_to_vk(post_text, image_source):
    attachments = []
    if image_source:
            attachments.append(upload_photo_for_wall(image_source))
    response = vk_call(
        'wall.post',
        {
            'owner_id': -VK_GROUP_ID,
            'from_group': 1,
            'message': post_text or '',
            'attachments': ','.join(attachments) if attachments else None,
        },
    )
    post_id = response.get('post_id') if isinstance(response, dict) else None
    return post_id
