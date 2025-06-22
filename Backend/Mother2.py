import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import time
import random
import json
import threading
from queue import Queue
from config import get_openai_api_key

# Try to import the real assistant, fallback to demo if there are issues
try:
    from lapa import UrbanDataAssistant
    REAL_ASSISTANT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Could not import UrbanDataAssistant: {e}")
    REAL_ASSISTANT_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Global streaming state
streaming_sessions = {}

class StreamingHybridAssistant:
    """Hybrid assistant with real-time streaming capabilities"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.mode = "initializing"
        self.real_assistant = None
        self.file_count = 0
        self.setup_assistant()
    
    def setup_assistant(self):
        """Try to setup real assistant, fallback to demo mode"""
        print("🔄 Initializing CityTalk Assistant...")
        
        # First try real OpenAI assistant if available
        if REAL_ASSISTANT_AVAILABLE and self.api_key:
            try:
                print("🌟 Attempting to use real OpenAI Assistant...")
                self.real_assistant = UrbanDataAssistant(self.api_key)
                
                if self.real_assistant.setup_assistant():
                    info = self.real_assistant.get_assistant_info()
                    self.file_count = info['files_uploaded']
                    self.mode = "openai"
                    print(f"✅ Real OpenAI Assistant ready! ({self.file_count} files)")
                    return
                else:
                    print("⚠️ OpenAI Assistant setup failed, switching to demo mode...")
                    
            except Exception as e:
                print(f"⚠️ OpenAI Assistant error: {e}")
                print("🔄 Falling back to demo mode...")
        
        # Fallback to demo mode
        self.setup_demo_mode()
    
    def setup_demo_mode(self):
        """Setup demo mode with simulated data"""
        self.mode = "demo"
        
        # Count real CSV files if available for demo realism
        try:
            data_dir = os.path.join("..", "Data")
            if not os.path.exists(data_dir):
                data_dir = "Data"
            
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
                self.file_count = len(csv_files)
                print(f"🎭 Demo mode initialized with {self.file_count} CSV files detected")
            else:
                self.file_count = 5  # Default demo count
                print("🎭 Demo mode initialized (no data directory found)")
                
        except Exception as e:
            self.file_count = 5
            print(f"🎭 Demo mode initialized with default settings: {e}")
    
    def process_query_streaming(self, user_query, session_id):
        """Process query with real-time streaming to frontend"""
        try:
            if self.mode == "openai" and self.real_assistant:
                return self._stream_openai_response(user_query, session_id)
            else:
                return self._stream_demo_response(user_query, session_id)
                
        except Exception as e:
            print(f"❌ Error in streaming query: {e}")
            return self._send_stream_error(session_id, str(e))
    
    def _stream_openai_response(self, user_query, session_id):
        """Stream real OpenAI response"""
        def stream_thread():
            try:
                queue = streaming_sessions[session_id]
                
                # Send initial status
                queue.put({
                    'type': 'status',
                    'message': '🤖 Connecting to OpenAI Assistant...'
                })
                
                # Use the streaming method from lapa.py
                # We need to modify lapa.py to support custom streaming callbacks
                result = self.real_assistant.process_query_simple(user_query)
                
                if result['success']:
                    # Simulate streaming for now (we can enhance this later)
                    response = result['response']
                    words = response.split()
                    
                    queue.put({
                        'type': 'start',
                        'message': '🤖 Assistant is writing...'
                    })
                    
                    current_text = ""
                    for i, word in enumerate(words):
                        current_text += word + " "
                        queue.put({
                            'type': 'content',
                            'content': current_text,
                            'progress': (i + 1) / len(words)
                        })
                        time.sleep(0.05)  # Simulate typing speed
                    
                    queue.put({
                        'type': 'complete',
                        'final_content': response,
                        'run_id': result.get('run_id', 'openai_complete')
                    })
                else:
                    queue.put({
                        'type': 'error',
                        'error': result['error']
                    })
                    
            except Exception as e:
                queue.put({
                    'type': 'error',
                    'error': f'OpenAI streaming error: {str(e)}'
                })
        
        # Start streaming in background thread
        thread = threading.Thread(target=stream_thread)
        thread.start()
    
    def _stream_demo_response(self, user_query, session_id):
        """Stream demo response with realistic typing effect"""
        def stream_thread():
            try:
                queue = streaming_sessions[session_id]
                
                # Send initial status
                queue.put({
                    'type': 'status',
                    'message': '🎭 Demo Assistant analyzing...'
                })
                
                time.sleep(1)  # Initial processing delay
                
                # Get demo response
                demo_result = self._get_demo_response(user_query)
                response = demo_result['response']
                
                queue.put({
                    'type': 'start',
                    'message': '🤖 Assistant is writing...'
                })
                
                # Stream the response word by word
                words = response.split()
                current_text = ""
                
                for i, word in enumerate(words):
                    current_text += word + " "
                    queue.put({
                        'type': 'content',
                        'content': current_text,
                        'progress': (i + 1) / len(words)
                    })
                    time.sleep(random.uniform(0.03, 0.08))  # Realistic typing speed
                
                queue.put({
                    'type': 'complete',
                    'final_content': response,
                    'run_id': demo_result['run_id']
                })
                
            except Exception as e:
                queue.put({
                    'type': 'error',
                    'error': f'Demo streaming error: {str(e)}'
                })
        
        # Start streaming in background thread
        thread = threading.Thread(target=stream_thread)
        thread.start()
    
    def _send_stream_error(self, session_id, error_msg):
        """Send error to streaming session"""
        if session_id in streaming_sessions:
            streaming_sessions[session_id].put({
                'type': 'error',
                'error': error_msg
            })
    
    def _get_demo_response(self, user_query):
        """Get demo response (same as before)"""
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['pollution', 'air quality', 'contamination']):
            response = """🏭 **Air Pollution Analysis - Barcelona**

**Data Processing Results:**
```python
import pandas as pd
import numpy as np

# Load and analyze pollution data
pollution_df = pd.read_csv('air_pollution_levels.csv')
barcelona_data = pollution_df[pollution_df['city'] == 'Barcelona']
print(f"Total monitoring stations: {len(barcelona_data)}")
```

**Key Findings:**
- 📊 Analyzed 3,847 pollution measurements
- 🏙️ 15 monitoring stations across Barcelona  
- 📈 PM2.5 levels: Eixample district highest (18.2 μg/m³)
- 🌿 Cleanest areas: Park Güell vicinity (12.1 μg/m³)
- 🛣️ Maragall street: Moderate levels (15.3 μg/m³)

**Recommendations for Low-Pollution Housing:**
1. Areas near Collserola Natural Park
2. Residential zones away from major traffic arteries
3. Properties with good ventilation systems
4. Avoid proximity to industrial zones

**Code Analysis:**
```python
# Filter for Maragall street area
maragall_area = barcelona_data[
    (barcelona_data['latitude'].between(41.4100, 41.4200)) &
    (barcelona_data['longitude'].between(2.1600, 2.1700))
]
low_pollution_properties = maragall_area[maragall_area['pm25'] < 16.0]
print(f"Found {len(low_pollution_properties)} suitable properties")
```"""
        else:
            response = f"""🏙️ **Urban Data Analysis** - "{user_query}"

**Data Processing Pipeline:**
```python
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Load Barcelona datasets
datasets = {{
    'pollution': pd.read_csv('air_pollution_levels.csv'),
    'bicing': pd.read_csv('bicing.csv'),
    'housing': pd.read_csv('Houses.csv'),
    'transport': pd.read_csv('PublicTransport.csv'),
    'bus_stops': pd.read_csv('ESTACIONS_BUS.csv')
}}

# Process query: {user_query}
results = analyze_urban_data(datasets, query="{user_query}")
```

**Available Datasets:**
- 🏭 **Air Pollution**: 3,847 measurements, 15 stations
- 🚴 **Bicing**: 467 bike stations, real-time availability
- 🏠 **Housing**: 2,341 properties, price & location data
- 🚇 **Transport**: Metro, bus, tram network data
- 🚌 **Bus Stops**: 2,800+ stops with frequency data

**Analysis Results:**
Based on the available data, I've identified relevant patterns and insights for your query. The analysis shows correlations between location, accessibility, and quality of life indicators in Barcelona.

**Recommendations:**
For more specific analysis, please provide details about your area of interest, time period, or specific metrics you'd like to explore."""
        
        return {
            'success': True,
            'response': response,
            'run_id': f"demo_run_{random.randint(1000, 9999)}"
        }
    
    def get_status(self):
        """Get current assistant status"""
        return {
            'mode': self.mode,
            'ready': True,
            'files_uploaded': self.file_count,
            'assistant_type': 'OpenAI GPT-4' if self.mode == 'openai' else 'Demo Assistant'
        }

# Initialize the streaming assistant
api_key = get_openai_api_key()
chat_assistant = StreamingHybridAssistant(api_key)

@app.route('/stream/<session_id>')
def stream_response(session_id):
    """Server-Sent Events endpoint for real-time streaming"""
    def generate():
        if session_id not in streaming_sessions:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Session not found'})}\n\n"
            return
        
        queue = streaming_sessions[session_id]
        
        while True:
            try:
                # Get message from queue (blocks until available)
                message = queue.get(timeout=30)  # 30 second timeout
                yield f"data: {json.dumps(message)}\n\n"
                
                # End stream on completion or error
                if message['type'] in ['complete', 'error']:
                    break
                    
            except:
                # Timeout or error - end stream
                yield f"data: {json.dumps({'type': 'timeout'})}\n\n"
                break
        
        # Clean up session
        if session_id in streaming_sessions:
            del streaming_sessions[session_id]
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
    })

@app.route('/process-prompt', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        user_query = data.get('prompt', '')
        use_streaming = data.get('streaming', True)  # Default to streaming
        
        if not user_query:
            return jsonify({'error': 'No prompt provided'}), 400
        
        print(f"\n🔹 Processing user query: {user_query}")
        
        if use_streaming:
            # Create streaming session
            session_id = f"session_{random.randint(10000, 99999)}_{int(time.time())}"
            streaming_sessions[session_id] = Queue()
            
            # Start streaming process
            chat_assistant.process_query_streaming(user_query, session_id)
            
            # Return streaming info
            status = chat_assistant.get_status()
            return jsonify({
                'streaming': True,
                'session_id': session_id,
                'stream_url': f'/stream/{session_id}',
                'mode': status['mode'],
                'assistant_type': status['assistant_type']
            })
        else:
            # Non-streaming fallback (for compatibility)
            return process_prompt_classic()
        
    except Exception as e:
        print(f"❌ Error processing prompt: {e}")
        return jsonify({'error': str(e)}), 500

def process_prompt_classic():
    """Classic non-streaming processing for fallback"""
    return jsonify({'error': 'Non-streaming mode not implemented. Please use streaming mode.'}), 400

@app.route('/health')
def health_check():
    status = chat_assistant.get_status()
    return jsonify({
        'status': 'healthy', 
        'assistant_ready': status['ready'],
        'files_uploaded': status['files_uploaded'],
        'mode': status['mode'],
        'assistant_type': status['assistant_type'],
        'streaming_available': True
    })

@app.route('/maps/<filename>')
def serve_map(filename):
    """Serve a simple default page instead of actual maps"""
    status = chat_assistant.get_status()
    mode_text = "Real AI Analysis" if status['mode'] == 'openai' else "Demo Mode"
    
    default_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CityTalk</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .message {{
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }}
            .mode {{
                font-size: 0.9em;
                opacity: 0.8;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="message">
            <h1>🏙️ CityTalk</h1>
            <p>Urban Data Analysis Assistant</p>
            <p>✨ Real-time Streaming Enabled!</p>
            <div class="mode">
                <strong>Mode:</strong> {mode_text}<br>
                <strong>Files:</strong> {status['files_uploaded']} CSV datasets
            </div>
        </div>
    </body>
    </html>
    """
    
    return Response(default_html, mimetype='text/html')

if __name__ == '__main__':
    status = chat_assistant.get_status()
    print("🚀 Starting CityTalk Streaming Backend...")
    print("📁 Available endpoints:")
    print("  - POST /process-prompt (Streaming chat processing)")
    print("  - GET /stream/<session_id> (SSE streaming endpoint)")
    print("  - GET /health (Health check)")
    print("  - GET /maps/<filename> (Default page)")
    print(f"🤖 Assistant Mode: {status['assistant_type']}")
    print(f"📊 Files Available: {status['files_uploaded']} CSV datasets")
    print("✨ Real-time streaming enabled!")
    app.run(debug=True, host='127.0.0.1', port=5000)