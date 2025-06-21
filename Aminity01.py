from BaseAgent import BaseAgent
import re
import requests
class AmenityAgent(BaseAgent):
    def __init__(self, api_key):
        self.pre_prompt = (
            "Detect the place names in the user's prompt in Barcelona. "
            "Return only the place names in a comma-separated List. "
            "All locations are in Barcelona; there may be one or more than one. only return the name of the location which was mentiond in the prompt also if you find bicing station in the prompt don't return it."
        )
        personality = (
            "You are a smart, advanced AI agent specialized in finding places."
        )
        self.mixed_prompt = "wf"
        super().__init__(api_key, model="gpt-3.5-turbo", personality=personality, pre_prompt=self.pre_prompt)
        self.coordinates = {}
        

    def extract_place_names(self, prompt):
        response = self.send_prompt(prompt)
        place_names = [name.strip() for name in response.split(",")]   
        print(place_names)
        return place_names

    def get_coordinates(self, place_name):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name,
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
            "viewbox": "2.05,41.47,2.23,41.32",  # Barcelona bounding box
            "bounded": 1
        }
       
        response = requests.get(url, params=params, headers={"User-Agent": "geo_agent"})
        data = response.json()
        if data:
            place = data[0]
            return {
                "name": place.get("display_name"),
                "lat": place.get("lat"),
                "lon": place.get("lon"),
                "osm_type": place.get("osm_type"),
                "osm_id": place.get("osm_id")
            }
        else:
            return None
    def return_mixed_prompt(self):
        """
        Replaces each place name in the prompt with the name + its coordinates.
        Ensures only whole-word matches are replaced to avoid overlapping issues.
        """
        # Initialize mixed_prompt to self.mixed_prompt (or self.prompt if mixed_prompt is not set)
        mixed_prompt = getattr(self, 'mixed_prompt', self.prompt)
        for name, coord in self.coordinates.items():
            pattern = r'\b' + re.escape(name) + r'\b'
            replacement = f"{name} (lat: {coord['lat']}, lon: {coord['lon']})"
            mixed_prompt = re.sub(pattern, replacement, mixed_prompt)
        return mixed_prompt
    
    def find_coordinates_for_prompt(self, prompt):
        """
        High-level function: detects place names and returns coordinates for each.
        Stores the results in self.coordinates.
        """
        self.prompt = prompt
        self.coordinates.clear()  # Clear previous data
        place_names = self.extract_place_names(prompt)
        for name in place_names:
            coord = self.get_coordinates(name)
            if coord:
                self.coordinates[name] = coord
        
        # Start with the original prompt
        self.mixed_prompt = self.prompt
        
        # If no locations were found (self.coordinates is empty), leave mixed_prompt as the original prompt.
        if not self.coordinates:
            return self.coordinates
        
        # Replace each place name with its coordinates
        for name, coord in self.coordinates.items():
            pattern = r'\b' + re.escape(name) + r'\b'
            replacement = f"{name} (lat: {coord['lat']}, lon: {coord['lon']})"
            self.mixed_prompt = re.sub(pattern, replacement, self.mixed_prompt)
        
        return self.coordinates





