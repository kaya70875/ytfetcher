import pytest
import httpx
from ytfetcher._youtube_v3 import YoutubeV3
from pytest_mock import MockerFixture
from ytfetcher.exceptions import InvalidApiKey, InvalidChannel, MaxResultsExceed, NoChannelVideosFound

@pytest.fixture
def youtubev3(mocker: MockerFixture):
    return YoutubeV3("test", "channel")

def test_invalid_api_key_with_403(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 403

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3(api_key="fake", channel_name="channel")

    with pytest.raises(InvalidApiKey):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()

def test_invalid_api_key_with_400(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 400

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3(api_key="fake", channel_name="channel")

    with pytest.raises(InvalidApiKey):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()

def test_invalid_channel_name(mocker: MockerFixture):
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {'kind': 'youtube#channelListResponse', 'etag': 'RuuXzTIr0OoDqI4S0RU6n4FqKEM', 'pageInfo': {'totalResults': 0, 'resultsPerPage': 5}}

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)
    youtube = YoutubeV3("api_key", "none_channel")

    with pytest.raises(InvalidChannel):
        youtube._get_channel_id()
    
    mock_get.assert_called_once()

def test_maximum_results_exceeded():
    with pytest.raises(MaxResultsExceed):
        YoutubeV3("test", "channel", [], 600)

def test_fetch_with_custom_video_ids_called(mocker: MockerFixture, youtubev3):
    youtubev3.video_ids = ["abc123", "def456"]
    mocker.patch.object(youtubev3, "_get_channel_id", return_value="dummy_channel_id")

    mock_fetch_with_custom = mocker.patch.object(
        youtubev3, "_fetch_with_custom_video_ids", return_value="video_data"
    )

    result = youtubev3.fetch_channel_snippets()

    mock_fetch_with_custom.assert_called_once()
    assert result == "video_data"

def test_fetch_with_playlist_id(mocker: MockerFixture, youtubev3):
    youtubev3.video_ids = []
    youtubev3.channel_name = 'channel'

    mocker.patch.object(youtubev3, '_get_channel_id', return_value="dummy_channel_id")
    mocker.patch.object(youtubev3, '_get_upload_playlist_id', return_value='playlist_id')
    mock_fetch_with_playlist = mocker.patch.object(youtubev3, '_fetch_with_playlist_id', return_value = 'video_data')

    result = youtubev3.fetch_channel_snippets()

    mock_fetch_with_playlist.assert_called_once()
    assert result == 'video_data'

def test_fetch_with_playlist_id_pagination(mocker: MockerFixture, youtubev3):
    youtubev3.video_ids = []
    youtubev3.max_results = 100

    first_response = {
        "items": [{
            "snippet": {
                "title": "Video 1",
                "description": "Desc",
                "publishedAt": "2021-01-01T00:00:00Z",
                "channelId": "abc",
                "thumbnails": {'default': {'url': 'url1', 'width': 10, 'height': 20}},
                "resourceId": {"videoId": "vid1"}
            }
        }],
        "nextPageToken": "PAGE_2"
    }

    second_response = {
        "items": [{
            "snippet": {
                "title": "Video 2",
                "description": "Desc",
                "publishedAt": "2021-01-02T00:00:00Z",
                "channelId": "abc",
                "thumbnails": {'default': {'url': 'url1', 'width': 10, 'height': 20}},
                "resourceId": {"videoId": "vid2"}
            }
        }]
    }

    mock_response_1 = mocker.Mock(spec=httpx.Response)
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = first_response

    mock_response_2 = mocker.Mock(spec=httpx.Response)
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = second_response

    mock_get = mocker.patch("httpx.Client.get", side_effect=[mock_response_1, mock_response_2])

    results = youtubev3._fetch_with_playlist_id("playlist_id")

    assert results[0].video_id == "vid1"
    assert results[0].metadata.title == "Video 1"
    assert results[1].metadata.title == "Video 2"
    assert mock_get.call_count == 2

def test_fetch_with_playlist_id_404_response(mocker: MockerFixture, youtubev3):
    youtubev3.video_ids = []
    youtubev3.max_results = 10

    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 404

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(NoChannelVideosFound):
        youtubev3._fetch_with_playlist_id("playlist_id")

def test_fetch_with_custom_invalid_video_ids(mocker: MockerFixture, youtubev3):
    youtubev3.video_ids = ['invalid1', 'invalid2']

    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {'kind': 'youtube#videoListResponse', 'etag': 'YIUPVpqNjppyCWOZfL-19bLb7uk', 'items': [], 'pageInfo': {'totalResults': 0, 'resultsPerPage': 0}}

    mocker.patch("httpx.Client.get", return_value=mock_response)

    results = youtubev3._fetch_with_custom_video_ids()
    assert results == []

def test_get_channel_id_method(mocker: MockerFixture, youtubev3):

    youtubev3.video_ids = []
    youtubev3.max_results = 10

    mock_response = mocker.Mock(spec=httpx.Response)
    mocker.patch('httpx.Client.get', return_value=mock_response)

    mock_response.status_code = 200
    mock_response.json.return_value = {'kind': 'youtube#channelListResponse', 'etag': 'eyEjTjtQvyjb1u1P9zafwf2xkgg', 'pageInfo': {'totalResults': 1, 'resultsPerPage': 5}, 'items': [{'kind': 'youtube#channel', 'etag': 'w3LqL8EL71QTkSoGxenzQwxJbxQ', 'id': 'UCa90xqK2odw1KV5wHU9WRhg'}]}
    assert youtubev3._get_channel_id() == 'UCa90xqK2odw1KV5wHU9WRhg'

def test_fetch_with_custom_invalid_and_valid_video_ids(mocker: MockerFixture, youtubev3):
    pass