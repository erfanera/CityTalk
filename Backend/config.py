import os
from pathlib import Path

def load_env_file(file_path=".env"):
    """Load environment variables from a .env file"""
    env_path = Path(file_path)
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def get_openai_api_key():
    """Get OpenAI API key from environment variables"""
    # Try to load from .env file first
    env_file_path = Path(__file__).parent.parent / ".env"
    load_env_file(env_file_path)
    
    # Get the API key from environment
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please create a .env file in the project root "
            "with OPENAI_API_KEY=your-api-key-here"
        )
    
    return api_key 