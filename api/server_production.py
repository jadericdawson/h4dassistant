import os
import json
import time
import sys
from pathlib import Path

# The 'send_from_directory' is added for serving the frontend
from flask import Flask, Response, request, stream_with_context, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
from rich import print as rprint
from rich.markdown import Markdown

# --- Flask App Initialization ---
# Get the absolute path of the directory where this script is located (api/)
basedir = os.path.abspath(os.path.dirname(__file__))
# Construct a robust, absolute path to the React build folder
static_folder_path = os.path.join(basedir, '../modern-chatbot/build')

# Use the absolute path to initialize the Flask app
app = Flask(__name__, static_folder=static_folder_path)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

# --- Load Environment Variables and OpenAI Client ---
# Load from .env file inside the 'api' directory
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    rprint("[bold red]FATAL: OPENAI_API_KEY not found in .env file.[/bold red]")
    exit(1)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- Configuration (Identical to your original script) ---
# The path is now relative to this script inside the 'api' folder.
BOOK_DATA_FILE_PATH = "kindle_book_data.json"
VECTOR_STORE_NAME = "Kindle Book Data Hybrid Assistant Store"
ASSISTANT_NAME = "Kindle Book QA Hybrid Assistant"
ASSISTANT_MODEL = "gpt-4.1" # Preserved from your script
RETRIEVAL_MODEL = "gpt-4.1" # Preserved from your script

# --- Global Variables for Server State ---
GLOBAL_VECTOR_STORE_ID = None
ASSISTANT_ID = None

# --- Assistant Instructions and Tool Definitions (Identical to your script) ---
ASSISTANT_INSTRUCTIONS = (
    "You are a helpful assistant specialized in answering questions about a provided book. "
    "You have access to a custom tool called `retrieve_book_info` to find information from the book. "
    "When asked a question that requires information from the book, formulate a clear query and use the `retrieve_book_info` tool. "
    "The tool will return relevant text passages. Synthesize this information to provide a comprehensive answer. "
    "If a user asks you to perform a sequential task, such as 'elaborate on each H4D step one at a time' or 'go through points A, B, and C', "
    "you should aim to complete the entire sequence. "
    "After providing the information for one item in the sequence (e.g., Step 1), identify the next item (e.g., Step 2). "
    "Then, proactively use the `retrieve_book_info` tool to gather information for that *next* item and present its elaboration. "
    "Continue this process for all items in the requested sequence. Clearly indicate which item/step you are currently discussing. "
    "Assume common knowledge for standard sequences like numbered steps unless specified differently. "
    "If the initial information from a single tool call is insufficient for a particular step or query, you may use the `retrieve_book_info` tool again with a refined query for that *same* step. "
    "If the tool returns data with a 'text_content' field and potentially a 'citations' field including 'file_id' and 'quote', "
    "incorporate these details and cite the source text (e.g., '[Source: quote from file_id]'). "
    "If the tool indicates no relevant information was found after your attempts for a specific item, state that you couldn't find it in the book for that item. "
    "Always respond to user queries by directly answering their question based on the information you have or retrieve."
)

CUSTOM_RETRIEVAL_TOOL_DEFINITION = {
    "type": "function", "function": {
        "name": "retrieve_book_info",
        "description": "Retrieve information from the book's knowledge base using a query. Use this for questions about the book's content.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]}
    }
}

# --- Core Logic Functions (Functionality is identical to your script) ---

def get_or_create_vector_store_id():
    global GLOBAL_VECTOR_STORE_ID
    rprint(f"\n[bold blue]Step 1: Managing OpenAI Vector Store[/bold blue]")
    try:
        rprint(f"Searching for existing Vector Store named '{VECTOR_STORE_NAME}'...")
        list_response = openai_client.vector_stores.list(limit=100)
        for vs in list_response.data:
            if vs.name == VECTOR_STORE_NAME:
                GLOBAL_VECTOR_STORE_ID = vs.id
                rprint(f"[green]Found existing Vector Store: '{VECTOR_STORE_NAME}' (ID: {vs.id})[/green]")
                return vs.id
        rprint(f"Vector Store '{VECTOR_STORE_NAME}' not found. Creating a new one...")
        vector_store = openai_client.vector_stores.create(name=VECTOR_STORE_NAME)
        GLOBAL_VECTOR_STORE_ID = vector_store.id
        rprint(f"[green]Created new Vector Store: '{VECTOR_STORE_NAME}' (ID: {vector_store.id})[/green]")
        return vector_store.id
    except Exception as e:
        rprint(f"[red]Error managing vector stores:[/red] {e}"); return None

def upload_data_file_to_vector_store(vector_store_id):
    if not vector_store_id: return False
    data_file_path = Path(BOOK_DATA_FILE_PATH)
    if not data_file_path.exists():
        rprint(f"[red]Error: Book data file not found at {data_file_path}.[/red]"); return False
    rprint(f"Attempting to ensure '{data_file_path.name}' is in Vector Store '{vector_store_id}'...")
    try:
        existing_vs_files = openai_client.vector_stores.files.list(vector_store_id=vector_store_id, limit=100)
        for vs_file_entry in existing_vs_files.data:
            try:
                file_metadata = openai_client.files.retrieve(file_id=vs_file_entry.id)
                if file_metadata.filename == data_file_path.name and vs_file_entry.status == 'completed':
                    rprint(f"[green]Found existing '{data_file_path.name}' (ID: {vs_file_entry.id}) already processed.[/green]")
                    return True
            except Exception: pass
        rprint(f"'{data_file_path.name}' not found. Proceeding with upload.")
        with open(data_file_path, "rb") as f_rb:
            uploaded_file_obj = openai_client.files.create(file=f_rb, purpose="assistants")
        
        openai_client.vector_stores.files.create(vector_store_id=vector_store_id, file_id=uploaded_file_obj.id)
        
        rprint("Waiting for file to be processed...")
        start_time = time.time()
        while True:
            vs_file_status = openai_client.vector_stores.files.retrieve(vector_store_id=vector_store_id, file_id=uploaded_file_obj.id)
            rprint(f"File processing status: {vs_file_status.status} (elapsed: {int(time.time() - start_time)}s)")
            if vs_file_status.status == "completed":
                rprint("[bold green]File successfully processed![/bold green]"); return True
            elif vs_file_status.status == "failed":
                rprint(f"[bold red]File processing failed: {vs_file_status.last_error}[/bold red]"); return False
            if time.time() - start_time > 300:
                rprint("[bold red]Timeout waiting for file processing.[/bold red]"); return False
            time.sleep(10)
    except Exception as e:
        rprint(f"[red]Error during file upload: {e}[/red]"); return False

def retrieve_book_info(query: str, max_results: int = 10):
    if not GLOBAL_VECTOR_STORE_ID:
        return json.dumps({"status": "error", "message": "Knowledge base not configured."})
    
    max_results = min(max(1, max_results), 10)
    file_search_tool_for_responses = { "type": "file_search", "vector_store_ids": [GLOBAL_VECTOR_STORE_ID], "max_num_results": max_results }
    try:
        response_api_call = openai_client.responses.create(model=RETRIEVAL_MODEL, input=query, tools=[file_search_tool_for_responses])
        processed_results = []
        for output_element in response_api_call.output:
            if output_element.type == "message" and output_element.content:
                for content_item in output_element.content:
                    if content_item.type == 'output_text':
                        processed_results.append({"text_content": content_item.text})
        if processed_results:
            return json.dumps({"status": "success", "retrieved_passages": processed_results})
        else:
            return json.dumps({"status": "no_data", "message": "No relevant text found."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Tool execution failed: {e}"})

available_functions = { "retrieve_book_info": retrieve_book_info }

def get_or_create_assistant():
    global ASSISTANT_ID
    rprint(f"\n[bold blue]Step 2: Managing OpenAI Assistant[/bold blue]")
    try:
        rprint(f"Searching for existing Assistant named '{ASSISTANT_NAME}'...")
        list_response = openai_client.beta.assistants.list(limit=100)
        assistant = next((a for a in list_response.data if a.name == ASSISTANT_NAME), None)
        
        if assistant:
            rprint(f"[green]Found Assistant '{ASSISTANT_NAME}' (ID: {assistant.id}). Updating...[/green]")
            updated_asst = openai_client.beta.assistants.update(
                assistant.id, name=ASSISTANT_NAME, model=ASSISTANT_MODEL,
                instructions=ASSISTANT_INSTRUCTIONS, tools=[CUSTOM_RETRIEVAL_TOOL_DEFINITION]
            )
            ASSISTANT_ID = updated_asst.id
            rprint(f"[green]Assistant updated.[/green]")
        else:
            rprint(f"Assistant '{ASSISTANT_NAME}' not found. Creating a new one...")
            new_asst = openai_client.beta.assistants.create(
                name=ASSISTANT_NAME, model=ASSISTANT_MODEL,
                instructions=ASSISTANT_INSTRUCTIONS, tools=[CUSTOM_RETRIEVAL_TOOL_DEFINITION]
            )
            ASSISTANT_ID = new_asst.id
            rprint(f"[green]Created new Assistant: '{ASSISTANT_NAME}' (ID: {new_asst.id})[/green]")
        return ASSISTANT_ID
    except Exception as e:
        rprint(f"[red]Error managing Assistant: {e}[/red]"); return None

def initialize_server():
    rprint("[magenta]Initializing server...[/magenta]")
    if not Path(BOOK_DATA_FILE_PATH).exists():
        rprint(f"[bold red]FATAL: Book data file not found at {Path(BOOK_DATA_FILE_PATH).resolve()}. Exiting.[/bold red]"); exit(1)
    vector_store_id = get_or_create_vector_store_id()
    if not vector_store_id: exit(1)
    if not upload_data_file_to_vector_store(vector_store_id):
        rprint("[bold red]FATAL: Failed to upload data file. Exiting.[/bold red]"); exit(1)
    assistant_id = get_or_create_assistant()
    if not assistant_id: exit(1)
    rprint(f"\n[bold cyan]--- Server Initialized. Ready for requests ---[/bold cyan]")

# --- API Endpoint (Unchanged) ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    thread_id = data.get('thread_id')

    if not user_message: return Response(json.dumps({"error": "Message is required"}), status=400, mimetype='application/json')

    def generate_responses():
        def yield_event(event_type: str, content: any = "", thread_id_to_send: str = None):
            payload = {"type": event_type, "content": content}
            if thread_id_to_send: payload["thread_id"] = thread_id_to_send
            yield f"data: {json.dumps(payload)}\n\n"

        current_thread = None
        try:
            if thread_id:
                try: current_thread = openai_client.beta.threads.retrieve(thread_id)
                except Exception: current_thread = None
            
            if not current_thread:
                yield from yield_event("thinking", "New thread created.")
                current_thread = openai_client.beta.threads.create()
                yield from yield_event("thread_created", thread_id_to_send=current_thread.id)

            openai_client.beta.threads.messages.create(thread_id=current_thread.id, role="user", content=user_message)
            yield from yield_event("thinking", "User message added. Running assistant...")
            
            run = openai_client.beta.threads.runs.create(thread_id=current_thread.id, assistant_id=ASSISTANT_ID)
            
            while run.status in ['queued', 'in_progress', 'requires_action']:
                if run.status == 'requires_action':
                    yield from yield_event("thinking", "Run requires tool call(s).")
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        if tool_call.type == "function":
                            func_name = tool_call.function.name
                            if func_name in available_functions:
                                func_args = json.loads(tool_call.function.arguments)
                                yield from yield_event("thinking", f"Assistant calling: {func_name}({func_args})")
                                yield from yield_event("thinking", f"Tool: '{func_name}' | Query: '{func_args.get('query')}' | Max results: {func_args.get('max_results', 10)}")
                                
                                output_str = available_functions[func_name](**func_args)
                                tool_outputs.append({"tool_call_id": tool_call.id, "output": output_str})
                    
                    if tool_outputs:
                        run = openai_client.beta.threads.runs.submit_tool_outputs(thread_id=current_thread.id, run_id=run.id, tool_outputs=tool_outputs)
                        yield from yield_event("thinking", "Tool outputs submitted. Continuing run...")
                
                time.sleep(1) 
                run = openai_client.beta.threads.runs.retrieve(thread_id=current_thread.id, run_id=run.id)

            if run.status == 'completed':
                messages = openai_client.beta.threads.messages.list(thread_id=current_thread.id, order="desc", limit=1)
                assistant_message = messages.data[0].content[0].text.value
                yield from yield_event("final", {"format": "markdown", "text": assistant_message})
            else:
                yield from yield_event("error", f"Run failed with status: {run.status}")

        except Exception as e:
            yield from yield_event("error", f"An unexpected error occurred: {e}")

    return Response(stream_with_context(generate_responses()), mimetype='text/event-stream')


# --- NEW: Serve React App ---
# This is the new section that serves the production frontend.
# It handles all requests that don't match the '/api/chat' route.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if not os.path.exists(app.static_folder):
        return "Static folder not found.", 404
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return "index.html not found in build folder.", 404
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    try:
        initialize_server()
        # For production, we bind to 0.0.0.0 to be accessible by the tunnel
        app.run(host='0.0.0.0', port=5055, debug=False, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            rprint("[bold red]FATAL: Port 5055 is already in use by another program.[/bold red]")
            rprint("Please find and stop that program before restarting.")
            sys.exit(1)
        else:
            raise
