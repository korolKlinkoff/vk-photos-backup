from config import settings
import requests
import json
from datetime import datetime


def get_photo_info(item):
    """
    vk photo item -> {photo: str, likes: int, date: datetime}
    """
    my_item = {
        "photo": item["orig_photo"]["url"],
        "likes": item["likes"]["count"],
        "date": datetime.fromtimestamp(item["date"])
    }
    return my_item


class VkClient:
    def __init__(self, token, version='5.199'):
        self.token = token
        self.version = version
        self.base_params = {'access_token': token, 'v': self.version}
        self.base_url = "https://api.vk.com/method"

    def _url_constructor(self, path):
        return self.base_url + path

    def photos_get(self, user_id, album_id):
        response = requests.get(self._url_constructor("/photos.get"), {**self.base_params, 'owner_id': user_id,
                                                                       'album_id': album_id, 'extended': True})
        return response


class YDiscClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.base_headers = {'Authorization': self.token}
        self.base_params = {}

    def _url_constructor(self, path):
        url = self.base_url + path
        return url

    def create_dir(self, dir_name):
        params = self.base_params
        params["path"] = "/" + dir_name
        response = requests.put(self._url_constructor("/resources"),
                                params={**self.base_params, "path": f"/{dir_name}"}, headers=self.base_headers)
        return response

    def upload_photo(self, photo_bytes, name, _directory=""):
        path = f'/{_directory}{name}{settings.FILE_EXTENSION}'
        params = {**self.base_params, "path": path}
        upload_url = requests.get(self._url_constructor("/resources/upload"), params,
                                  headers=self.base_headers).json()
        response = requests.put(upload_url["href"], photo_bytes)
        if response.status_code == 201:
            print(f"successfully uploaded {path}")
        return requests.put(upload_url["href"], photo_bytes)


if __name__ == '__main__':
    vk_user_id = input("VK user id: ")
    new_yandex_token = input("yandex disk token (leave empty for .env one): ")
    if new_yandex_token:
        settings.YANDEX_TOKEN = new_yandex_token

    vk_client = VkClient(settings.VK_TOKEN)
    y_client = YDiscClient(settings.YANDEX_TOKEN)

    profile_photos = vk_client.photos_get(vk_user_id, "profile").json()["response"]["items"]

    # list of all photos (includes ones we need date for)
    photos_data = [get_photo_info(i) for i in profile_photos]

    photos_likes = [x["likes"] for x in photos_data]
    photos_names = []

    for n, photo in enumerate(photos_data):
        if photo["likes"] in photos_likes[:n]:
            photo['name'] = f"{str(photo['likes'])} {str(photo['date'].date())}"
        else:
            photo['name'] = str(photo['likes'])

        # in case of several photos uploaded at the same date
        if photo['name'] in photos_names:
            i = 1
            while f"{photo['name']} {i}" in photos_names:
                i = i + 1
            photo['name'] = f"{photo['name']} {i}"

        photos_names.append(photo['name'])

    # pprint(photos_data)

    output = []
    y_client.create_dir("backup images")
    for photo in photos_data:
        image = requests.get(photo["photo"]).content
        size = len(image)
        output.append({"file_name": photo["name"], "size": size})
        y_client.upload_photo(image, photo["name"], "backup images/")

    with open(settings.OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f)
