import httpx
from ytfetcher.types.channel import ChannelData

class YoutubeV3:
    def __init__(self, api_key: str, snippets: dict):
        self.api_key = api_key
        self.snippets = snippets
    
    def fetch_channel_snippets(self, channel_id: str):
        """
        Get all channel snippets from a YouTube channel using the YouTube Data API v3.
        """

        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': self.api_key
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            res = response.json()
            uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            return self._fetch_with_playlist_id(uploads_playlist_id, self.max_results)
    
    def _fetch_with_playlist_id(self, uploads_playlist_id: str) -> ChannelData:
        try:
            data = {
                'video_ids' : [],
                'metadata' : []
            }
            base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            next_page_token = None

            with httpx.Client(timeout=self.timeout) as client:
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
            print('total videos fetched: ',len(data['video_ids']))
            return ChannelData(**data)
        except AttributeError as attr_err:
            print('Error fetching video IDs:', attr_err)
            return ChannelData(video_ids=[], metadata=[])