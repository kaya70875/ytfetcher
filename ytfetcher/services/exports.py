from ytfetcher.types.channel import FetchAndMetaResponse

class Exporter:
    def __init__(self, channel_data: FetchAndMetaResponse, allowed_metadata_list: list, timing: bool):
        self.channel_data = channel_data
        self.allowed_metadata_list = allowed_metadata_list
        self.timing = timing
    
    def export_as_txt(self):
        pass

    def export_as_json(self):
        pass

    def export_as_csv(self):
        pass