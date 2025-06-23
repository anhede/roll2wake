import urequests as requests
from server.models import StoryBeat
from client.wifi_client import WifiClient
from server.stats import Statistics

class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_new_story(self) -> StoryBeat:
        """Get a new story from the API"""
        try:
            response = requests.get(f"{self.base_url}/new")
            #response.raise_for_status()
            data = response.json()
            beat = StoryBeat.from_dict(data['story_beat'])
            return beat
        except Exception as e:
            print(f"Error: {e}")
            print(data) # type: ignore
            raise e

    def update_story(self, choice_id: int, success_result: str) -> StoryBeat:
        """Update the story with a choice and result"""
        try:
            response = requests.post(f"{self.base_url}/update", json={"choice_id": choice_id, "success_result": success_result})
            #response.raise_for_status()
            data = response.json()
            beat = StoryBeat.from_dict(data['story_beat'])
            return beat
        except Exception as e:
            print(f"Error: {e}")
            raise e
        
    def publish_statistics(self, stat: Statistics) -> None:
        """Publish statistics to the server"""
        try:
            requests.post(f"{self.base_url}/stats", json=stat.to_dict())
            print(f"Statistics published: {stat.to_dict()}")
        except Exception as e:
            print(f"Error publishing statistics: {e}")
            raise e

if __name__ == "__main__":
    from components.utils import get_iso_timestamp
    wifi_client = WifiClient()
    client = Client("http://192.168.1.234:5000")
    beat = client.get_new_story()
    print(beat.full_format())
    beat = client.update_story(1, "success")
    print(beat.full_format())
    stat = Statistics("test_stat", 42.0, get_iso_timestamp())
    client.publish_statistics(stat)