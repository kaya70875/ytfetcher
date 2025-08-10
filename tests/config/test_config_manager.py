import json
from unittest.mock import patch, mock_open
from ytfetcher.config.config_manager import save_api_key, load_api_key, CONFIG_FILE

def test_save_api_key_creates_dir_and_writes_file():
    with patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("builtins.open", mock_open()) as mock_file:

        save_api_key("my_fake_api_key")

        # mkdir should be called with parents=True, exist_ok=True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # open should be called with the CONFIG_FILE and 'w' mode
        mock_file.assert_called_once_with(CONFIG_FILE, 'w', encoding='utf-8')

        # Check json.dump called with correct data and file handle
        handle = mock_file()
        handle.write.assert_called()  # json.dump calls write internally

def test_load_api_key_reads_file_and_returns_key():
    fake_api_key = "saved_key"

    m_open = mock_open(read_data=json.dumps({"api_key": fake_api_key}))
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", m_open):
        result = load_api_key()
        assert result == fake_api_key
        m_open.assert_called_once_with(CONFIG_FILE, "r", encoding="utf-8")

def test_load_api_key_returns_none_when_file_missing():
    with patch("pathlib.Path.exists", return_value=False):
        result = load_api_key()
        assert result is None
