from BaseAgent import BaseAgent
from Aminity01 import AmenityAgent
from Data02 import DataLayerAgent
from DataReader import DataReaderAgent
from DataCollect03 import DataCollectorAgent
import pandas as pd
# from MainAgent import MainAgent
from lapa import MainAgent
from Viz01 import save_kepler_map, display_html_with_custom_style

# 1️⃣ Initialize agents
# api_key = "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"  # make sure it's valid
amenity_agent = AmenityAgent(api_key)
data_layer_agent = DataLayerAgent(api_key)
data_collector_agent = DataCollectorAgent(api_key, data_dir="./CSV")
# 2️⃣ User prompt
user_query = "find 20 houses that are least exposed to polution in  Maragall street in barcelona "

# 3️⃣ Step 1: Use AmenityAgent to extract coordinates
print("\n🔹 Using AmenityAgent...")
coordinates = amenity_agent.find_coordinates_for_prompt(user_query)
print("📌 Coordinates found:", coordinates)
mixed_prompt = amenity_agent.return_mixed_prompt()
print("🧠 Mixed prompt with coordinates:", mixed_prompt)

# 4️⃣ Step 2: Use DataLayerAgent to determine datasets
print("\n🔹 Using DataLayerAgent...")
dataset_info = data_layer_agent.identify_datasets(mixed_prompt)
print("🗂️ Datasets identified:", dataset_info["datasets"])
print("📄 Explanation:", dataset_info["explanation"])

# 5️⃣ Step 3: Use DataCollectorAgent to fetch data
print("\n🔹 Using DataCollectorAgent...")
fetched_data = data_collector_agent.fetch_data(dataset_info["datasets"], coordinates)
all_data, csv_dirs = data_collector_agent.fetch_data(dataset_info["datasets"], coordinates)
# print(all_data.keys())
# # Example: if any "other" dataset was found
# if csv_dirs:
#     print("\n📁 Found CSV paths:")
#     for tag, path in csv_dirs.items():
#         print(f"- {tag}: {path}")
# 5️⃣ Step 4: Use add description to the data
data_reader_agent = DataReaderAgent(api_key)
Nice_Dataset = data_reader_agent.create_dataset_with_analysis(all_data)

# 6️⃣ Step 5: Use MainAgent to execute the code with coordinates  
main_agent = MainAgent(api_key)

execution_result = main_agent.execute_question(user_query, Nice_Dataset)
# print(execution_result)
# 6️⃣ Merge and display
# if fetched_data:
#     merged_df = pd.concat(fetched_data, ignore_index=True)
#     print("\n✅ Final merged data:")
#     print(merged_df.head())
# else:
#     print("\n⚠️ No data found for the given query.")
map_path, map_filename = save_kepler_map(all_data)
display_html_with_custom_style(map_path)
print(f"🌐 Map saved and ready at: {map_path}")