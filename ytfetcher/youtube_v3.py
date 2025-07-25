import httpx
from tqdm import tqdm  # type: ignore
from ytfetcher.types.channel import ChannelData
from ytfetcher.exceptions import InvalidChannel, InvalidApiKey, MaxResultsExceed, NoChannelVideosFound


class YoutubeV3:
    """
    A wrapper for interacting with the YouTube Data API v3.

    Supports fetching video metadata either by channel handle or by specific video IDs.
    Provides functionality to retrieve channel ID, uploads playlist ID, and video snippets.

    Parameters:
        api_key (str): A valid YouTube Data API v3 key.
        channel_name (str): YouTube channel handle (e.g. '@veritasium').
        video_ids (list[str]): Optional list of video IDs to fetch metadata for.
        max_results (int): Maximum number of videos to fetch (must be between 1 and 500).

    Raises:
        MaxResultsExceed: If max_results is greater than 500 or less than 1.
    """

    def __init__(self, api_key: str, channel_name: str, video_ids: list[str] = [], max_results: int = 50):
        self.api_key = api_key
        self.channel_name = channel_name
        self.video_ids = video_ids
        self.max_results = max_results

        if not (1 <= self.max_results <= 500):
            raise MaxResultsExceed("You can only fetch 500 videos per channel.")

    def fetch_channel_snippets(self) -> ChannelData:
        """
        Fetches video snippets and metadata for the given channel or custom video IDs.

        If video IDs were provided during initialization, those will be used.
        Otherwise, it fetches the channel ID, retrieves the uploads playlist,
        and pulls video metadata from it.

        Returns:
            ChannelData: An object containing video IDs and their metadata.
        """
        channel_id = self._get_channel_id()

        if self.video_ids:
            return self._fetch_with_custom_video_ids()

        uploads_playlist_id = self._get_upload_playlist_id(channel_id)
        return self._fetch_with_playlist_id(uploads_playlist_id)

    def _fetch_with_playlist_id(self, uploads_playlist_id: str) -> ChannelData:
        """
        Fetches video IDs and metadata from a YouTube uploads playlist.

        This method uses the YouTube Data API to iterate through playlist items
        and collect video metadata up to `self.max_results`.

        Parameters:
            uploads_playlist_id (str): The ID of the uploads playlist to fetch from.

        Returns:
            ChannelData: Contains a list of video IDs and their corresponding metadata.

        Raises:
            NoChannelVideosFound: If the playlist is not found (HTTP 404).
        """
        try:
            video_ids = []
            metadata = []

            base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            next_page_token = None

            with httpx.Client() as client, tqdm(desc='Fetching snippets', unit='video', total=self.max_results) as pbar:
                while True:
                    params = {
                        'part': 'snippet',
                        'playlistId': uploads_playlist_id,
                        'maxResults': 50,
                        'pageToken': next_page_token,
                        'key': self.api_key,
                        'fields': 'items(snippet(title,description,publishedAt,channelId,thumbnails,resourceId/videoId)),nextPageToken'
                    }

                    response = client.get(base_url, params=params)
                    res = response.json()

                    if response.status_code == 404:
                        raise NoChannelVideosFound()

                    for item in res['items']:
                        if len(video_ids) >= self.max_results:
                            break
                        video_id = item['snippet']['resourceId']['videoId']
                        snippet = item['snippet']

                        video_ids.append(video_id)
                        metadata.append(snippet)

                        pbar.update(1)
                    next_page_token = res.get('nextPageToken')
                    if not next_page_token:
                        break
            return ChannelData(video_ids=video_ids, metadata=metadata)
        except AttributeError as attr_err:
            print('Error fetching video IDs:', attr_err)
            return ChannelData(video_ids=[], metadata=[])

    def _fetch_with_custom_video_ids(self) -> ChannelData:
        """
        Fetches video metadata for the list of provided video IDs.

        Uses the YouTube Data API to retrieve snippets for each video ID given.

        Returns:
            ChannelData: Contains the original video IDs and their corresponding metadata.
        """
        try:
            metadata = []

            base_url = 'https://www.googleapis.com/youtube/v3/videos'

            with httpx.Client() as client:
                params = {
                    'part': 'snippet',
                    'id': [*self.video_ids],
                    'key': self.api_key,
                }

                response = client.get(base_url, params=params)
                res = response.json()

                for item in res['items']:
                    snippet = item['snippet']
                    metadata.append(snippet)

            return ChannelData(video_ids=self.video_ids, metadata=metadata)
        except AttributeError as attr_err:
            print('Error fetching video IDs:', attr_err)
            return ChannelData(video_ids=[], metadata=[])

    def _get_upload_playlist_id(self, channel_id: str) -> str:
        """
        Retrieves the 'uploads' playlist ID for a given YouTube channel ID.

        Parameters:
            channel_id (str): The channel ID.

        Returns:
            str: The uploads playlist ID for the channel.
        """
        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': self.api_key
        }

        with httpx.Client() as client:
            response = client.get(url, params=params)
            res = response.json()
            uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return uploads_playlist_id

    def _get_channel_id(self) -> str:
        """
        Retrieves the YouTube channel ID using the channel handle.

        Returns:
            str: The channel ID.

        Raises:
            InvalidApiKey: If the provided API key is invalid.
            InvalidChannel: If the channel handle is not found.
        """
        with httpx.Client() as client:
            response = client.get(
                'https://www.googleapis.com/youtube/v3/channels',
                params={
                    'part': 'id',
                    'forHandle': f'@{self.channel_name}',
                    'key': self.api_key
                }
            )

            if response.status_code in {400, 403}:
                raise InvalidApiKey("Your API key is invalid.")

            response.raise_for_status()
            res = response.json()

            if 'items' in res and res['items']:
                return res['items'][0]['id']
            else:
                raise InvalidChannel(f"Channel '{self.channel_name}' not found.")
