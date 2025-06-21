from BaseAgent import BaseAgent
import pandas as pd

class DataReaderAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.model = "gpt-3.5-turbo"

    def analyze_dataset(self, dataset_dict):
        """
        Analyzes each dataset in the dictionary using GPT-3.5 Turbo.
        Returns a dictionary with dataset names as keys and their analysis as values.
        """
        analysis_results = {}
        
        for dataset_name, data in dataset_dict.items():
            print(f"📊 Analyzing dataset: {dataset_name}")
            
            # Create prompt for GPT-3.5 Turbo
            prompt = f"""
            Analyze this dataset and provide a clear, structured description of its contents.
            
            Dataset Name: {dataset_name}
            Number of Records: {len(data)}
            Columns: {list(data.columns)}
            
            Column Data Types:
            {data.dtypes.to_string()}
            
            Please provide:
            1. A brief overview of what this dataset contains
            2. Description of each column and its purpose
            3. Any notable patterns or characteristics in the data structure
            4. Potential use cases for this data
            
            Format the response in a clear, structured way.
            """
            
            # Get analysis from GPT
            try:
                analysis = self.send_prompt(prompt)
                analysis_results[dataset_name] = analysis
            except Exception as e:
                print(f"❌ Error analyzing {dataset_name}: {str(e)}")
                analysis_results[dataset_name] = f"Error during analysis: {str(e)}"
        print("aada"+analysis_results[dataset_name])
        return analysis_results

    def create_dataset_with_analysis(self, dataset_dict):
        """
        Creates a new dictionary where each value is a tuple containing:
        1. The original dataset
        2. The GPT analysis of the dataset
        
        Returns:
        dict: {dataset_name: (dataset, analysis)}
        """
        # First get the analysis for all datasets
        analysis_results = self.analyze_dataset(dataset_dict)
        
        # Create new dictionary with (dataset, analysis) tuples
        enriched_datasets = {}
        for dataset_name, dataset in dataset_dict.items():
            analysis = analysis_results.get(dataset_name, "Analysis not available")
            enriched_datasets[dataset_name] = (dataset, analysis)
            
        return enriched_datasets

    def analyze_single_column(self, dataset_name, data, column_name):
        """
        Analyzes a specific column in a dataset using GPT-3.5 Turbo.
        """
        if column_name not in data.columns:
            return f"Column '{column_name}' not found in dataset."
        
        column_data = data[column_name]
        
        prompt = f"""
        Analyze this column from the dataset:
        
        Dataset: {dataset_name}
        Column Name: {column_name}
        Data Type: {column_data.dtype}
        Non-null Count: {column_data.count()}
        Unique Values Count: {column_data.nunique()}
        Sample Values: {column_data.dropna().head(5).tolist()}
        
        Please provide:
        1. What this column represents
        2. The type of data it contains
        3. Any patterns or characteristics in the values
        4. Potential uses for this column in analysis
        
        Format the response in a clear, structured way.
        """
        
        try:
            return self.send_prompt(prompt)
        except Exception as e:
            return f"Error analyzing column: {str(e)}"
