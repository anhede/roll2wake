import urequests as requests
from server.models import StoryBeat
from client.wifi_client import WifiClient

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
            print(data)
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

if __name__ == "__main__":
    wifi_client = WifiClient()
    client = Client("http://192.168.1.137:5000")
    beat = client.get_new_story()
    print(beat.full_format())
    beat = client.update_story(1, "success")
    print(beat.full_format())
    beat = client.update_story(2, "success")
    print(beat.full_format())