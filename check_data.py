from DataCollect03 import DataCollectorAgent
from DataReader import DataReaderAgent
import pandas as pd
import geopandas as gpd

try:
    # Initialize DataCollector
    collector = DataCollectorAgent('dummy_key')
    
    # Define test datasets and coordinates (similar to your actual usage)
    datasets = [
        {"name": "Park Locations", "source": "osm", "location": {"latitude": 41.4005, "longitude": 2.2017}},
        {"name": "School Locations", "source": "osm", "location": {"latitude": 41.4005, "longitude": 2.2017}},
        {"name": "pollution", "source": "csv", "tag": "air_pollution_levels"}
    ]
    
    coordinates = {
        "El Poblenou": {"lat": 41.4005, "lon": 2.2017}
    }
    
    # Fetch data
    print("Fetching datasets...")
    datasets_info, csv_dirs = collector.fetch_data(datasets, coordinates)
    
    print("="*50)
    print("DATASET ANALYSIS")
    print("="*50)
    
    for name, dataset in datasets_info.items():
        print(f'\n=== {name} ===')
        print(f'Type: {type(dataset)}')
        
        if hasattr(dataset, 'shape'):
            print(f'Shape: {dataset.shape}')
        
        if hasattr(dataset, 'columns'):
            print(f'Columns: {list(dataset.columns)}')
            
            # Check if it's a GeoDataFrame
            if isinstance(dataset, gpd.GeoDataFrame):
                print(f'Geometry types: {dataset.geometry.geom_type.unique()}')
                print(f'CRS: {dataset.crs}')
            
            # Special handling for pollution data
            if 'pollution' in name.lower():
                print(f'First row sample:')
                for col in dataset.columns[:5]:  # First 5 columns
                    try:
                        sample_val = str(dataset[col].iloc[0])
                        if len(sample_val) > 100:
                            sample_val = sample_val[:100] + "..."
                        print(f'  {col}: {sample_val}')
                    except:
                        print(f'  {col}: [Error reading value]')
        
        print("-" * 30)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 