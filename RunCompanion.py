# Whole buncha libraries
from typing_extensions import override
from openai import AssistantEventHandler
from openai import OpenAI
from datetime import datetime
from pathlib import Path
import pytz
import json
import googlemaps
import requests
import platform
import os
import loggerfunc


# API KEYS!!!
OPENAI_API_KEY = "sk-testbot-streamlit-frontend-HzUx6rXxeWnOG3SbjTxnT3BlbkFJsm1UlvZiBUB6nG7nMEUU"
ASSISTANT_ID = "asst_Y6F5Bo6Z4EvYbBLfnRHcezj0"
WEATHERAPI = "OUxps2wwiS3iaHcFp181nC9fwzBZn41V"
GOOGLE_API = "AIzaSyA_kRS905tOffopwMYuYB93Ay7gjDPDPTs"
SERPAPI = "037BF1BBDE3C474C921D60770D1D9208"


# Long Term Memory File
memories_file = "memory.txt"
# Notes File
notes_file = "notes.txt"

# Initialize APIs
client = OpenAI(api_key=OPENAI_API_KEY)
gmaps = googlemaps.Client(key=GOOGLE_API)

# Function Definitions
def get_coords(): # Gets Latitude and Longitude of user
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
        print(f"Latitude: {lat}, Longitude: {long}")
        return f"Latitude: {lat}, Longitude: {long}"
    else:
        print("Could not determine the latitude and longitude.")
        return "Could not determine the latitude and longitude."

def get_current_city(): # Gets the city of the user's current location
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
    else:
        print("Could not determine the latitude and longitude.")
        return "City name could not be determined."
    reverse_geocode_result = gmaps.reverse_geocode((lat, long))
    city = None
    for component in reverse_geocode_result[0]['address_components']:
        if 'locality' in component['types']:
            city = component['long_name']
            break
    if city is not None:
        return city
    else:
        return "City name could not be determined."

def get_current_location(): # Gets the current location of the user
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
    else:
        print("Could not determine the latitude and longitude.")
        return "Location could not be determined."
    
    reverse_geocode_result = gmaps.reverse_geocode((lat, long))
    
    if reverse_geocode_result and 'formatted_address' in reverse_geocode_result[0]:
        return reverse_geocode_result[0]['formatted_address']
    else:
        return "Address could not be determined."
        
def get_exact_location(): # Gets the exact location of the user. This functions almost identically to above but relays more information and thus uses more tokens when called by the assistant
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
    else:
        print("Could not determine the latitude and longitude.")
        return "Location could not be determined."
    
    reverse_geocode_result = gmaps.reverse_geocode((lat, long))
    return reverse_geocode_result

def get_device_info(): # Gets some basic info about the device running this script
    dev_info = f"Architecture:{platform.machine()} - OS:{platform.system()}"
    return dev_info

def get_current_time(): # Gets the current time from the user's device
    return datetime.now().isoformat()

def get_latitude(): # Gets the user's current latitude
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        return lat
    else:
        print("Could not determine latitude.")
        return "Could not determine latitude."
    
def get_longitude(): # Gets the user's current longitude
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lng' in geolocation_result['location']:
        long = geolocation_result['location']['lng']
        return long
    else:
        print("Could not determine the longitude.")
        return "Could not determine the longitude."

def new_note(note_to_add): # Writes a new line to the notes file
    try:
        notes = open(notes_file, "a")
        notes.write(note_to_add)
        print(f"{note_to_add} succesfully appended to note file")
        notes.close()
    except Exception as e:
        print(f"Failed to append note to note file. Reason:{e}")
        return f"Failed to append note to note file. Reason:{e}"

def overwrite_note(note_to_replace): # Overwrites the notes file
    try:
        notes = open(notes_file, "w")
        notes.write(note_to_replace)
        print(f"Succesfully overwrote notes with {note_to_replace}")
        notes.close()
    except Exception as e:
        print(f"Failed to overwrite note file. Reason:{e}")
        return f"Failed to overwrite note file. Reason:{e}"

def commit_memory(memory_to_commit): # Writes a new line to the memory file
    try:
        memories = open(memories_file, "a")
        memories.write(memory_to_commit)
        print(f"{memory_to_commit} succesfully commited to memory")
        memories.close()
    except Exception as e:
        print(f"Failed to commit {memory_to_commit} to long term memory. Reason:{e}")
        return f"Failed to commit {memory_to_commit} to long term memory. Reason:{e}"

def overwrite_memory(new_memory): # Overwrites memory file
    try:
        memories = open(memories_file, "w")
        memories.write(new_memory)
        print(f"Succesfully overwrote memory with {new_memory}")
        memories.close()
    except Exception as e:
        print(f"Failed to overwrite memory file. Reason:{e}")
        return f"Failed to overwrite memory file. Reason:{e}"

def cls(): # Function for clearing the screen
    os.system('cls' if os.name=='nt' else 'clear')

# Retrieve Assistant from OpenAI
try:
    assistant = client.beta.assistants.retrieve(assistant_id=ASSISTANT_ID)
except Exception as e:
    print(f"Failed to retrieve OpenAI Assistant: {e}")

# Create an EventHandler class to handle assistant responses and function calls
class EventHandler(AssistantEventHandler):
  # Handle new text generated
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
    loggerfunc.log(f"{delta.value}", thread_id)
  # Handle assistant call for function
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  # Handle if run state changes to 'requires_action'
  def on_event(self, event):
    # Retrieve events that are denoted with 'requires_action'
    # since these will have our tool_calls
    if event.event == 'thread.run.requires_action':
      run_id = event.data.id  # Retrieve the run ID from the event data
      self.handle_requires_action(event.data, run_id)
    elif event.event == 'thread.run.completed':
      loggerfunc.newline(thread_id)
    elif event.event == 'thread.run.queued':
      loggerfunc.log("Assistant: ", thread_id)
  # Function Call Handler
  def handle_requires_action(self, data, run_id):
    tool_outputs = []
     
    for tool in data.required_action.submit_tool_outputs.tool_calls:
      
      print(f"Tool Name: {json.dumps(tool.function.name)}") # Debugging printout
      print(f"Tool Arguments:{json.dumps(tool.function.arguments)}") # Debugging printout
      loggerfunc.newline(thread_id)
      loggerfunc.log("TOOL CALL/n", thread_id)
      loggerfunc.log(f"Tool Name: {json.dumps(tool.function.name)}", thread_id)
      
      # Split tool call into tool name and arguments provided
      arguments = json.loads(tool.function.arguments) if isinstance(tool.function.arguments, str) else tool.function.arguments
      
      print(f"Parsed Arguments:{arguments}") # Debugging printout
      loggerfunc.log(f"\nParsed Arguments:{arguments}", thread_id)
      print("-----------------------------------------------")
      
      if tool.function.name == "get_time":
        # Parse arguments into internal variable
        timezone_str = arguments.get("time_zone", "UTC")
        
        try:
          timezone = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
          tool_outputs.append({"tool_call_id": tool.id, "output": "Timezone unrecognized. Please use a timezone in the pytz python library. e.g. America/New York"})
        
        now = datetime.now(timezone)
        time_format = arguments.get("format", "12hr")
        
        if time_format == "12hr":
          current_time = now.strftime('%H:%M:%S')
        elif time_format == "24hr":
          current_time = now.strftime('%H:%M:%S')
        else:
          current_time = now.strftime('%H:%M:%S')
          
        tool_outputs.append({"tool_call_id": tool.id, "output": f"The current time in {timezone_str} is: {current_time}"})
      
      elif tool.function.name == "get_date":
        # Parse arguments into internal variable
        timezone_str = arguments.get("time_zone", "UTC")

        try:
          timezone = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
          tool_outputs.append({"tool_call_id": tool.id, "output": "Timezone unrecognized. Please use a timezone in the pytz python library."})
          
        now = datetime.now(timezone)
        current_date = now.strftime('%d:%m:%Y')
        tool_outputs.append({"tool_call_id": tool.id, "output": f"The current time in {timezone_str} is: {current_date}"})
      
      elif tool.function.name == "get_exact_loc":
        tool_outputs.append({"tool_call_id": tool.id, "output": f"{get_exact_location()}"})
      
      elif tool.function.name == "get_current_weather":
        # Parse arguments into internal variable
        latlong = arguments.get("location", "42.3478,-71.0466")
        unit = arguments.get("unit", "f")
        timestep = arguments.get("timestep", "hourly")
        
        # Parse Timestep variable for forecasting
        if timestep == "daily":
            query_timestep = "1d"
            print("Timestep accepted. Getting daily forecast.")
        elif timestep == "hourly":
            query_timestep = "1h"
            print("Timestep accepted. Getting hourly forecast.")
        else:
            query_timestep = "1d"
            print("Timestep is invalid. Defaulting to daily forecast.")
            
        # Parse Unit variable for API call
        if unit == "f":
            query_unit = "imperial"
            print("Unit type accepted. Using Imperial system.")
        elif unit == "c":
            query_unit = "metric"
            print("Unit type accepted. Using Metric system.")
        else:
            query_unit = "imperial"
            print("Unit type is invalid. Defaulting to Imperial units.")
        
        # Generate API Call
        weather_base_url = "https://api.tomorrow.io/v4/weather/forecast?"
        complete_url = weather_base_url + "location=" + latlong +"&timesteps=" + query_timestep + "&units=" + query_unit + "&apikey=" + WEATHERAPI
        weather_response = requests.get(complete_url)
        weather_data = weather_response.json()
        
        tool_outputs.append({"tool_call_id": tool.id, "output": f"Latitude and longitude: {latlong} Unit: {query_unit} Weather Data: {weather_data}"})
        
      elif tool.function.name == "convert_to_coords":
        # Parse arguments into internal variables
        city_name = arguments.get("city_name", "0")
        
        geocode_result = gmaps.geocode(city_name)
        
        loca = geocode_result[0]['geometry']['location']
        lat = loca['lat']
        long = loca['lng']
        
        tool_outputs.append({"tool_call_id": tool.id, "output": f"The coordinates of {city_name} are {lat},{long}"})
      
      elif tool.function.name == "convert_city":
        # Parse arguments into internal variables
        latitude = arguments.get("latitude", "0")
        longitude = arguments.get("longitude", "0")
        
        reverse_geocode_result = f"{gmaps.reverse_geocode((latitude, longitude))}" # Use Google API to get reverse geocode result
        
        tool_outputs.append({"tool_call_id": tool.id, "output": reverse_geocode_result})
      
      elif tool.function.name == "new_note":
        # Parse arguments into internal variables
        notea = arguments.get("note_to_add", "None")
        # Attempt to append note onto notes file 
        try:
            new_note(f"\n{notea}")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Added '{notea}' to notes file."})
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to append '{notea}' to notes file. Reason: {e}"})
            print(f"TOOL OUTPUT: Failed to append '{notea}' to notes file. Reason: {e}")
      
      elif tool.function.name == "overwrite_notes":
        # Parse arguments into internal variables
        notea = arguments.get("notes_to_replace_with", "")
        # Attempt to delete line from notes file 
        try:
            overwrite_note(notea)
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Replaced notes with {notea}"})
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to overwrite notes file. Reason: {e}"})
            print(f"TOOL OUTPUT: Failed to overwrite notes file. Reason: {e}")
      
      elif tool.function.name == "read_notes":
        try:
            notes = open(notes_file, "r")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Notes File Content: {notes.read()}"})
            notes.close()
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to retrieve {notes_file}. Reason: {e}"})
            print(f"Failed to retrieve {notes_file}. Reason: {e}")
      
      elif tool.function.name == "new_memory":
        # Parse arguments into internal variables
        memorya = arguments.get("memory_to_commit", "None")
        # Attempt to append note onto notes file 
        try:
            commit_memory(f"/n{memorya}")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Added '{memorya}' to notes file."})
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to append '{memorya}' to notes file. Reason: {e}"})
            print(f"TOOL OUTPUT: Failed to append '{memorya}' to notes file. Reason: {e}")
      
      elif tool.function.name == "overwrite_memory":
        # Parse arguments into internal variables
        memorya = arguments.get("memories", "")
        # Attempt to overwrite memory
        try:
            overwrite_memory(memorya)
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Replaced notes with {memorya}"})
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to overwrite memory file. Reason: {e}"})
            print(f"TOOL OUTPUT: Failed to overwrite memory file. Reason: {e}")
      
      elif tool.function.name == "read_memories":
        try:
            memories = open(memories_file, "r")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Memory File Content: {memories.read()}"})
            memories.close()
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to retrieve Memories. Reason: {e}"})
            print(f"Failed to retrieve Memories. Reason: {e}")
      
      elif tool.function.name == "create_file":
        file_type = arguments.get("file_type", "txt")
        file_name = arguments.get("file_name", "test")
        file_content = arguments.get("file_content", "test")
        file_write_type = arguments.get("file_write_type", "t")
        try:
            file = open(f"{file_name}.{file_type}", f"w{file_write_type}")
            file.write(file_content)
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Created file with name ({file_name}.{file_type}) and content {file_content}"})
            file.close()
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to create file with name {file_name}.{file_type}. Reason: {e}"})
            print(f"Failed to create file with name {file_name}.{file_type}. Reason: {e}")
      
      elif tool.function.name == "read_file":
        file_path = arguments.get("file_name", "")
        try:
            file = open(file_path, "r")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"{file_path} Content: {file.read()}"})
            file.close()
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to retrieve {file_path}. Reason: {e}"})
            print(f"Failed to retrieve {file_path}. Reason: {e}")
      
      elif tool.function.name == "modify_file":
        file_content = arguments.get("file_content", "")
        file_name = arguments.get("file_name", "test")
        try:
            file = open(file_name, "w")
            file.write(file_content)
            print(f"Succesfully replaced {file_name} content with: {file_content}")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Replaced {file_name} content with: {file_content}"})
            file.close()
        except Exception as e:
            print(f"Failed to overwrite {file_name}. Reason:{e}")
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Failed to replace {file_name} content with: {file_content} --------- Reason: {e}"})
      
      elif tool.function.name == "custom_api_call":
        call_url = arguments.get("call_url", "")
        call_type = arguments.get("call_type", "get")
        call_data = arguments.get("call_data", "")
        if call_type == "post":
            r = requests.post(call_url, call_data)
            data = r.json()
            tool_outputs.append({"tool_call_id": tool.id, "output": f"API Response: {data}"})
        elif call_type == "get":
            r = requests.get(call_url, call_data)
            data = r.json()
            tool_outputs.append({"tool_call_id": tool.id, "output": f"API Response: {data}"})
        else:
            tool_outputs.append({"tool_call_id": tool.id, "output": "Invalid call type. Please use POST or GET."})
      
      elif tool.function.name == "search":
        try:
            search = arguments.get("query", "")
        
            search_api_url = "https://api.scaleserp.com/search?api_key="
            assembled_url = search_api_url + SERPAPI + "&q=" + search
            
            data_received = requests.get(assembled_url)
            data_string = data_received.json()
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Search Results: {data_string}"})
        except Exception as e:
            tool_outputs.append({"tool_call_id": tool.id, "output": f"Search failed. Reason {e}"})
      
      elif tool.function.name == "test_tools":
        tool_outputs.append({"tool_call_id": tool.id, "output": "Current script is capable of handling tool calls."}) # Tell assistant the current script is capable of handling tool calls
        print(f"TOOL OUTPUT: Test tool processed and ran succesfully") # Debugging printout
        print(" ")
        print("-----------------------------------------------")
      
      # catch all for invalid tool calls. Sends the assistant a response saying the tool was invalid so it won't use it again during current thread.
      else:
        tool_outputs.append({"tool_call_id": tool.id, "output": "Function Invalid. Wrong Script?"}) # Tell assistant the function called is invalid or can not be handled by the current script
        print("Tool Call Was Invalid") # Debugging printout
    
    self.submit_tool_outputs(tool_outputs, run_id) # Submit all tool_outputs at the same time
  # Submit all tool outputs function
  def submit_tool_outputs(self, tool_outputs, run_id):
    # Use the submit_tool_outputs_stream helper
    with client.beta.threads.runs.submit_tool_outputs_stream(
      thread_id=self.current_run.thread_id,
      run_id=self.current_run.id,
      tool_outputs=tool_outputs,
      event_handler=EventHandler(),
    ) as stream:
      for text in stream.text_deltas:
        pass



# Create thread and start chat to query assistant
def run_assistant():
    # Start Main Thread
    try:
        global thread_id
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(f"Created New Thread with ID: {thread.id}")
        print("Type '?' for help.")
    except Exception as e:
        print(f"Failed to create thread: {e}")
        return
    
    # Start Main Loop
    while True:
        # Set Variables and formatting
        print("-----------------------------------------------")
        user_data = f"<Location: {get_current_location()} Latitude:{get_latitude()} Longitude:{get_longitude()}><Device:{get_device_info()}><Query Time:{get_current_time()}>" # User data part of query
        user_input = input("You: ")
        
        # Split command or user query into individual words
        command_parts = user_input.split()
        command = command_parts[0].lower()
        arg1 = command_parts[1] if len(command_parts) > 1 else None
        arg2 = ' '.join(command_parts[2:])
        
        # Determine if user input is a command or a query
        if command in ["exit", "quit"]: # Exit Command
            print("Ending the conversation.")
            break
        elif command == "retrieve" and arg1: # Thread Retrieval Command
            try:
                thread = client.beta.threads.retrieve(thread_id=arg1)
                thread_id = thread.id
                print(f"Detached from old thread and attached to thread with ID: {thread.id}")
            except Exception as e:
                print(f"Failed to retrieve thread: {e}")
                print(f" Attaching to old thread with ID: {thread.id}")    
        elif command == "retrieve" and arg1 is None: # Handle retrieve usage if no arguments given
            print("No Thread ID Provided")
        elif command in ["clear"]: # Clear Thread Command
            cls()
            print(f"Closing current thread({thread_id}) and creating new one")
            try:
                thread = client.beta.threads.create()
                thread_id = thread.id
                print(f"Created New Thread with ID: {thread.id}")
            except Exception as e:
                print(f"Failed to create thread: {e}")
                return
        elif command == "upload" and arg1 and arg2:
            try:
                file = client.files.create(
                    file=Path(arg1),
                    purpose='assistants'
                )
                # Create array to store file IDs
                files_array = [f"{file.id}"]  # This should be a simple list of strings
                print(f"File Uploaded to OpenAI Assistant Successfully with ID: {file.id}")
                # Create Vector Store and attach File ID
                vector_store = client.beta.vector_stores.create(
                    name=f"Vector Store for Thread ID: {thread.id}",
                    file_ids=files_array,  # Passing simple list
                    expires_after={
                        "anchor": "last_active_at",
                        "days": 1
                    },
                )
                print(f"Vector Store Created Succesfully with ID: {vector_store.id}")
                try:
                    client.beta.threads.update(
                        thread_id,
                        tool_resources={
                            "file_search": {
                                "vector_store_ids": [vector_store.id], 
                            }
                        }
                    )
                    print(f"Vector Store with ID {vector_store.id} Attached Succesfully to Thread with ID {thread.id}")
                except Exception as e:
                    print(f"Vector Store Failed to Attach to Thread ID: {thread_id} for reason: {e}")
                
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"{arg2} `User Data: {user_data}`"
                )
                print(" ")
                print("-----------------------------------------------")
                # Create new EventHandler instance for each stream
                event_handler = EventHandler()
            
                # Stream the assistant's response
                with client.beta.threads.runs.stream(
                        thread_id=thread.id,
                        assistant_id=assistant.id,
                        event_handler=event_handler
                ) as stream:
                    stream.until_done()
                    print("")
                
            except Exception as e:
                print(f"File was not attached to Thread with ID {thread_id} Reason: {e}")
        elif command == "upload" and arg1 is None:
            print("No file provided.")
        elif command == "upload" and arg2 is None:
            print("No query provided.")
        elif command in ["help", "?"]: # Help Command
            print("Commands:")
            print("help/?                - lists this dialog")
            print("clear                 - deletes the current thread and creates a new one")
            print("retrieve (Thread ID)  - attaches to a predefined thread ID")
            print("upload (File) (Query) - Uploads a file to the assistant for it to analyze")
            print("exit                  - closes the program")
        else: # Query Assistant for everything else
            
            loggerfunc.log(f"User: {user_input}", thread_id)
            loggerfunc.newline(thread_id)
            
            # Add the user message to the thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"{user_input} `User Data: {user_data}`"
            )
            print(" ")
            print("-----------------------------------------------")
            
            # Create new EventHandler instance for each stream
            event_handler = EventHandler()
            
            # Stream the assistant's response
            with client.beta.threads.runs.stream(
                    thread_id=thread.id,
                    assistant_id=assistant.id,
                    event_handler=event_handler
            ) as stream:
                stream.until_done()
                print("")



# Start main loop
if __name__ == "__main__":
    run_assistant()