from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import os
import time
from config import get_openai_api_key

class UrbanDataAssistant:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = get_openai_api_key()
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.assistant = None
        self.thread = None
        self.file_ids = []
        
    def setup_assistant(self):
        """Setup OpenAI assistant with CSV files from Data directory"""
        try:
            # Get list of CSV files from Data directory
            data_dir = os.path.join("..", "Data")  # Go up one directory to find Data
            
            if not os.path.exists(data_dir):
                data_dir = "Data"  # Try current directory as fallback
            
            if not os.path.exists(data_dir):
                print(f"⚠️ Warning: Data directory not found at {data_dir}")
                return False
            
            # Loop through all files in the Data directory
            csv_files_found = []
            for filename in os.listdir(data_dir):
                if filename.endswith(".csv"):
                    file_path = os.path.join(data_dir, filename)
                    try:
                        # Create file in OpenAI and store ID
                        file = self.client.files.create(
                            file=open(file_path, "rb"),
                            purpose='Urban Analysis'
                        )
                        self.file_ids.append(file.id)
                        csv_files_found.append(filename)
                        print(f"✅ Uploaded: {filename}")
                    except Exception as e:
                        print(f"⚠️ Failed to upload {filename}: {e}")
            
            if not self.file_ids:
                print("❌ No CSV files were successfully uploaded")
                return False
            
            # Create assistant
            self.assistant = self.client.beta.assistants.create(
                name="Urban Data Analyst",
                description="You're an urban data analyst specialized in Barcelona city data. Analyze user queries based on the CSV files you have access to, write code to calculate and find answers, break down analysis in clear steps, execute the code, and explain results with detailed insights and recommendations.",
                model="gpt-4.1",
                tools=[{"type": "code_interpreter"}],
                tool_resources={
                    "code_interpreter": {
                        "file_ids": self.file_ids
                    }
                }
            )
            
            # Create thread
            self.thread = self.client.beta.threads.create()
            
            print(f"✅ Assistant created: {self.assistant.id}")
            print(f"✅ Thread created: {self.thread.id}")
            print(f"✅ Files uploaded: {len(csv_files_found)} CSV files")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up assistant: {e}")
            return False
    
    def process_query_simple(self, user_query):
        """Process query and return simple response (non-streaming)"""
        try:
            if not self.assistant or not self.thread:
                return {
                    'success': False,
                    'error': 'Assistant not properly initialized. Please check your API key.'
                }
            
            # Create message in thread
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="Urban Designer",
                content=user_query
            )
            
            # Create and run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions="Provide detailed analysis with step-by-step breakdown. Write and execute code when needed for data analysis. Explain methodology, show results clearly, and provide actionable insights."
            )
            
            # Wait for completion
            max_attempts = 60  # 60 seconds timeout
            attempts = 0
            while run.status in ['queued', 'in_progress', 'cancelling'] and attempts < max_attempts:
                time.sleep(1)
                attempts += 1
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                
                if attempts % 10 == 0:  # Progress indicator every 10 seconds
                    print(f"⏳ Processing... ({attempts}s)")
            
            if run.status == 'completed':
                # Retrieve messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id
                )
                
                # Get the latest assistant message
                latest_message = messages.data[0] if messages.data else None
                if latest_message and latest_message.role == 'assistant':
                    response_text = ""
                    for content in latest_message.content:
                        if content.type == 'text':
                            response_text += content.text.value
                    
                    return {
                        'success': True,
                        'response': response_text,
                        'run_id': run.id,
                        'status': run.status
                    }
            else:
                error_msg = f'Analysis failed with status: {run.status}'
                if attempts >= max_attempts:
                    error_msg += ' (timeout after 60 seconds)'
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing error: {str(e)}'
            }
    
    def process_query_streaming(self, user_query):
        """Process query with streaming response"""
        try:
            if not self.assistant or not self.thread:
                print("❌ Assistant not initialized")
                return
            
            # Create message in thread
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id, 
                role="user",
                content=user_query
            )
            
            class EventHandler(AssistantEventHandler):
                @override
                def on_text_created(self, text) -> None:
                    print(f"\n🤖 Assistant > ", end="", flush=True)

                @override
                def on_tool_call_created(self, tool_call):
                    print(f"\n🔧 {tool_call.type}\n", flush=True)

                @override
                def on_message_done(self, message) -> None:
                    # Print citations to files
                    message_content = message.content[0].text
                    annotations = message_content.annotations
                    citations = []
                    for index, annotation in enumerate(annotations):
                        message_content.value = message_content.value.replace(
                            annotation.text, f"[{index}]"
                        )
                        if file_citation := getattr(annotation, "file_citation", None):
                            cited_file = self.client.files.retrieve(file_citation.file_id)
                            citations.append(f"[{index}] {cited_file.filename}")

                    print(message_content.value)
                    if citations:
                        print("\n📚 Sources:")
                        print("\n".join(citations))

            # Stream the response
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions="Provide comprehensive urban data analysis with step-by-step code execution and clear explanations.",
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
                
        except Exception as e:
            print(f"❌ Streaming error: {e}")
    
    def get_assistant_info(self):
        """Get information about the assistant"""
        return {
            'assistant_id': self.assistant.id if self.assistant else None,
            'thread_id': self.thread.id if self.thread else None,
            'files_uploaded': len(self.file_ids),
            'ready': bool(self.assistant and self.thread)
        }

# Demo function - only runs when file is executed directly
def run_demo():
    """Demo function showing how to use the assistant"""
    api_key = get_openai_api_key()
    
    assistant = UrbanDataAssistant(api_key)
    
    if assistant.setup_assistant():
        print("\n" + "="*50)
        print("🏙️ Urban Data Assistant Ready!")
        print("="*50)
        
        # Example query
        query = "Find the top 5 bicing stations that are close to the most polluted areas"
        print(f"\n📝 Query: {query}")
        print("\n🔄 Processing with streaming response:")
        assistant.process_query_streaming(query)
    else:
        print("❌ Failed to initialize assistant")

# Only run demo if this file is executed directly
if __name__ == "__main__":
    run_demo()
