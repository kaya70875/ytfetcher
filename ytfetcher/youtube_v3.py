import httpx
from ytfetcher.types.channel import ChannelData
from ytfetcher.exceptions import InvalidChannel, InvalidApiKey, MaxResultsExceed

class YoutubeV3:
    def __init__(self, api_key: str, channel_name: str, video_ids: list[str] = [], max_results: int = 50):
        self.api_key = api_key
        self.channel_name = channel_name
        self.video_ids = video_ids
        self.max_results = max_results

        if not(1 <= self.max_results <= 500):
            raise MaxResultsExceed("You can only fetch 500 videos per channel.")
    
    def fetch_channel_snippets(self) -> ChannelData:
        """
        Get all channel snippets from a YouTube channel using the YouTube Data API v3.
        """

        channel_id = self._get_channel_id()

        if self.video_ids:
            return self._fetch_with_custom_video_ids()
        
        uploads_playlist_id = self._get_upload_playlist_id(channel_id)
        return self._fetch_with_playlist_id(uploads_playlist_id)
    
    def _fetch_with_playlist_id(self, uploads_playlist_id: str) -> ChannelData:
        try:
            data = {
                'video_ids' : [],
                'metadata' : []
            }
            base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            next_page_token = None

            with httpx.Client() as client:
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
                    for item in res['items']:
                        if len(data['video_ids']) >= self.max_results: break
                        video_id = item['snippet']['resourceId']['videoId']
                        snippet = item['snippet']

                        data['video_ids'].append(video_id)
                        data['metadata'].append(snippet)

                    next_page_token = res.get('nextPageToken')
                    if not next_page_token:
                        break
            return ChannelData(**data)
        except AttributeError as attr_err:
            print('Error fetching video IDs:', attr_err)
            return ChannelData(video_ids=[], metadata=[])
    
    def _fetch_with_custom_video_ids(self) -> ChannelData:
        try:
            data = {
                'video_ids' : self.video_ids,
                'metadata' : []
            }
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
                    data['metadata'].append(snippet)
                        
            return ChannelData(**data)
        except AttributeError as attr_err:
            print('Error fetching video IDs:', attr_err)
            return ChannelData(video_ids=[], metadata=[])
    
    def _get_upload_playlist_id(self, channel_id: str):
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
        with httpx.Client() as client:
            response = client.get(
                'https://www.googleapis.com/youtube/v3/channels',
                params={
                    'part': 'id',
                    'forHandle': f'@{self.channel_name}',
                    'key': self.api_key
                }
            )
            
            if response.status_code == 400 or response.status_code == 403:
                raise InvalidApiKey("Your api key is invalid.")

            response.raise_for_status()
            res = response.json()

            if 'items' in res and res['items']:
                return res['items'][0]['id']
            else:
                raise InvalidChannel(f"Channel '{self.channel_name}' not found.")