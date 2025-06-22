from BaseAgent import BaseAgent
from Aminity01 import AmenityAgent
from Data02 import DataLayerAgent
from DataReader import DataReaderAgent
from DataCollect03 import DataCollectorAgent
import pandas as pd
# from MainAgent import MainAgent
from lapa import MainAgent
from Viz01 import save_kepler_map, display_html_with_custom_style
from config import get_openai_api_key

# 1️⃣ Initialize agents
api_key = get_openai_api_key()

# 2️⃣ User prompt
user_query = "find 20 houses that are least exposed to polution in  Maragall street in barcelona "



# 5️⃣ Step 3: Use DataCollectorAgent to fetch data
# print("\n🔹 Using DataCollectorAgent...")
# fetched_data = data_collector_agent.fetch_data(dataset_info["datasets"], coordinates)
# all_data, csv_dirs = data_collector_agent.fetch_data(dataset_info["datasets"], coordinates)

# print("All data:", all_data)
# print("CSV dirs:", csv_dirs)
# print(all_data.keys())
# # Example: if any "other" dataset was found
# if csv_dirs:
#     print("\n📁 Found CSV paths:")
#     for tag, path in csv_dirs.items():
#         print(f"- {tag}: {path}")
# 5️⃣ Step 4: Use add description to the data



# 6️⃣ Step 5: Use MainAgent to execute the code with coordinates  
# main_agent = MainAgent(api_key)




# execution_result = main_agent.execute_question(user_query, Nice_Dataset)


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