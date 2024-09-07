import os
import dotenv


class Settings:
    def __init__(self):
        self.VK_TOKEN: str = os.environ["VK_TOKEN"]
        self.YANDEX_TOKEN: str = os.environ["YANDEX_TOKEN"]
        self.VK_APP_ID: int = int(os.environ["VK_APP_ID"])
        self.OUTPUT_PATH: str = os.environ["OUTPUT_PATH"]
        self.FILE_EXTENSION: str = os.environ["FILE_EXTENSION"]


dotenv.load_dotenv()
settings = Settings()
