import requests

VK_API_VERSION = '5.199'


def upload_photo_for_wall(image_source, vk_group_id, vk_api_token, vk_api_version=VK_API_VERSION):
    response = requests.post(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params={
            'group_id': vk_group_id,
            'access_token': vk_api_token,
            'v': vk_api_version,
        },
        timeout=30,
    )
    response.raise_for_status()
    vk_response = response.json()
    upload_url = vk_response['response']['upload_url']
    with open(image_source, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files, timeout=30)
        response.raise_for_status()
        upload_response = response.json()
    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params={
            'group_id': vk_group_id,
            'photo': upload_response['photo'],
            'server': upload_response['server'],
            'hash': upload_response['hash'],
            'access_token': vk_api_token,
            'v': vk_api_version,
        },
        timeout=30,
    )
    response.raise_for_status()
    saved = response.json()['response']
    photo = saved[0]
    return f"photo{photo['owner_id']}_{photo['id']}"


def publish_post_to_vk(post_text, image_source, vk_group_id, vk_api_token, vk_api_version=VK_API_VERSION):
    attachments = []
    if image_source:
        attachments.append(upload_photo_for_wall(image_source, vk_group_id, vk_api_token, vk_api_version))
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params={
            'owner_id': -vk_group_id,
            'from_group': 1,
            'message': post_text or '',
            'attachments': ','.join(attachments) if attachments else None,
            'access_token': vk_api_token,
            'v': vk_api_version,
        },
        timeout=30,
    )
    response.raise_for_status()
    vk_response = response.json()
    post_id = vk_response.get('response', {}).get('post_id')
    return post_id
