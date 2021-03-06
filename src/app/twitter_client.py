import os
import requests
from app.utils import get_random_string
from app.logger_client import LoggerClient


class TwitterClient:
    
    def __init__(self, config: dict, logger: LoggerClient, url: str):
        """
        Initializes the client for Twitter

        Args:
            config (dict): dictionary containing the keys. Comes from config.
                At the same time, config keys must be set as environment variables
            logger (LoggerClient): instance of the logger
            url (str): link to the tweet
        """
        self._url = url
        self._config = config.TWITTER_CONFIG
        self._logger = logger
        self._tweet_id = self._get_tweet_id()
    
    def _get_tweet_id(self):
        if '/' not in self._url:
            return None
        
        # The id can be found at the end of the url
        return self._url.split('/')[-1].split('?')[0]

    def _get_media_urls(self):
        """
        Builds the link for the API and harvests the content
        """
        if not self._tweet_id:
            return []

        headers = {'Authorization': f'Bearer {self._config["bearer_token"]}'}
        url = f"https://api.twitter.com/2/tweets/{self._tweet_id}?expansions=attachments.media_keys&media.fields=url"

        try:
            tweet_data = requests.get(url=url, headers=headers)
            
            # Ensure that we're getting response 200
            if tweet_data.status_code != 200:
                self._logger.error(f'Request not completed: {tweet_data}')
                return []
        
        except requests.exceptions.RequestException as e:
            self._logger.error(f"There was a problem with the request: {e}")
            return []
        
        media = tweet_data.json().get("includes", {}).get("media", {})
        return [m["url"] for m in media] if media else []

    def download_image(
        self,
        image_name: str = None,
        image_folder: str = 'images',
        image_format: str = '.jpg'
    ):
        """
        Downloads and save image(s) harvested from the tweet

        Arguments
        ---------
            - image_name: (str, optional): name for the image. When `None`, a
              random string will be set as name.

            - image_folder (str, optional): where to store the images.
              Defaults to 'images'.

            - image_format (str, optional): defaults to '.jpg'.
        """
        media_urls = self._get_media_urls()
        for url in media_urls:
            # Gather elements for image saving, save and print feedback
            if image_name is None:
                image_name = get_random_string()
            
            image_filename = f'{image_name}{image_format}'
            image_path = os.path.join(image_folder, image_filename)
            image_file = requests.get(url)

            with open(image_path, 'wb') as f:
                f.write(image_file.content)

            self._logger.info(f'Image saved at {image_path}')
