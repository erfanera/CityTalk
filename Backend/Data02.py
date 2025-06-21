from BaseAgent import BaseAgent
import json
class DataLayerAgent(BaseAgent):
    osm_features = {
        "parking_entrance", "ferry_terminal", "pharmacy", "cinema", "recycling", "drinking_water",
        "clinic", "fast_food", "parking", "post_box", "library", "bank", "place_of_worship", "theatre",
        "restaurant", "bar", "fuel", "telephone", "doctors", "taxi", "toilets", "vending_machine",
        "townhall", "bicycle_parking", "community_centre", "bicycle_rental", "cafe", "compressed_air",
        "post_office", "atm", "bench", "pub", "university", "car_sharing", "bureau_de_change",
        "ice_cream", "arts_centre", "school", "apartments", "stripclub", "brothel", "union", "college",
        "food_court", "fountain", "shelter", "kindergarten", "waste_disposal", "social_centre",
        "grit_bin", "language_school", "veterinary", "driving_school", "waste_basket",
        "conference_centre", "nightclub", "hospital", "police", "internet_cafe", "car_wash",
        "charging_station", "prep_school", "bbq", "dentist", "car_rental", "vacuum_cleaner",
        "training", "clock", "marketplace", "post_depot", "luggage_locker", "social_facility", "signs",
        "stock_exchange", "pastries", "music_school", "tap", "studio", "shower", "motorcycle_rental",
        "motorcycle_parking", "childcare", "bicycle_repair_station", "dormitory", "aparthotel",
        "monastery", "dancing_school", "courthouse", "water_point", "gambling", "vehicle_inspection",
        "love_hotel", "dance_school", "nursing_home", "warehouse", "coworking_space", "photo_booth",
        "research_institute", "dojo", "locker", "events_venue", "casino", "planetarium", "parking_space",
        "parcel_locker", "table", "bus_station", "bicycle_rental;left_luggage", "money_transfer",
        "beauty_school", "disused", "flight_attendant", "therapist", "public_bookcase", "sailing_school",
        "letter_box", "office", "swingers club", "watering_place", "relay_box", "exhibition_centre",
        "sanitary_dump_station", "grocery", "karaoke_box", "toy_library", "piano", "lounger",
        "hookah_lounge", "scooter_rental", "animal_shelter", "boat_rental", "wifi", "dressing_room",
        "loading_dock", "fixme", "boat_storage", "dive_centre", "surf_school", "kick-scooter_parking",
        "exhibition_hall", "fire_station", "public", "market", "grave_yard", "prison", "public_building",
        "place_of_mourning", "gym", "smoking_area", "crematorium", "workshop", "collection", "garden",
        "dog_toilet", "traffic_park", "ticket_validator", "park",
        "supermarket", "shop", "store", "retail", "commercial", "mall", "shopping",
        "residential", "building", "house", "home", "apartment", "housing", "villa", "cottage",
        "hotel", "motel", "hostel", "guesthouse", "accommodation", "lodging",
        "office_building", "commercial_building", "industrial", "warehouse", "factory",
        "attraction", "tourism", "landmark", "monument", "museum", "gallery",
        "transport", "station", "stop", "terminal", "subway", "train", "bus", "metro",
        "amenity", "facility", "service", "infrastructure", "utilities",
        "recreation", "leisure", "sports", "playground", "field", "court", "stadium",
        "water", "river", "lake", "pond", "fountain", "well", "spring",
        "street", "road", "highway", "path", "trail", "walkway", "sidewalk",
        "bridge", "tunnel", "crossing", "intersection", "roundabout"
    }


    def identify_datasets(self, user_query):
        prompt = f"""
        You are a data layer identification expert. Given the user's question,
        identify the types of data needed to answer it. Return a JSON object with:
        - name: The dataset name.
        - source: "osm" if it's an OpenStreetMap feature, otherwise "other".
        - tag: A simplified label (lowercase, no spaces) to help search for the file if source is "other".

        -Do not include place names (like city names, neighborhoods, or landmarks) as datasets. 
        Locations are already handled by another agent.
        Format:
        {{
            "datasets": [
                {{
                    "name": "Hospital Locations",
                    "source": "osm",
                    "tag": "hospital"
                }},
                {{
                    "name": "Air Pollution Levels",
                    "source": "other",
                    "tag": "pollution"
                }}
            ],
            "explanation": "Explain why these datasets are relevant."
        }}

        User question: "{user_query}"
        """

        response_text = self.send_prompt(prompt)
        try:
            result = json.loads(response_text)
            for dataset in result.get("datasets", []):
                name_lower = dataset.get("name", "").lower()
                is_osm = any(osm_feature in name_lower for osm_feature in self.osm_features)
                dataset["source"] = "osm" if is_osm else "other"

                # Set default tag if not provided
                if "tag" not in dataset or not dataset["tag"].strip():
                    dataset["tag"] = name_lower.replace(" ", "_")

            print("Identified datasets:", result["datasets"])
            print("Explanation:", result["explanation"])
            return result

        except Exception as e:
            print("❌ Error parsing LLM response:", e)
            print("Raw response:", response_text)
            return {
                "datasets": [],
                "explanation": "Could not parse the LLM response properly."
            }