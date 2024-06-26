# Whole buncha libraries
# Premade libraries
from typing_extensions import override
from openai import AssistantEventHandler
from openai import OpenAI
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Back, Style
from time import sleep
import pytz
import json
import googlemaps
import requests
import platform
import os
import pygame
import threading
import speech_recognition as sr
import keyboard
# Custom Libraries
import loggerfunc


# Load settings file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_APIKEY')
ASSISTANT_ID = os.getenv('ASSISTANTID')
WEATHERAPI = os.getenv('WEATHERAPI')
GOOGLE_API = os.getenv('GOOGLE_API')
SERPAPI = os.getenv('SERPAPI')
voice_model = os.getenv('voice_model')
notes_file = os.getenv('notes_file')
memories_file = os.getenv('memories_file')
model_name = os.getenv('MODEL')
instructions = os.getenv('INSTRUCTIONS')
name = os.getenv('NAME')
tools = os.getenv('TOOL_LIST')
max_tokens = os.getenv('max_tokens')
vmodel_name = os.getenv('VOICE_TEXTGEN_MODEL')
vinstructions = os.getenv('VOICE_INSTRUCTIONS')
vname = os.getenv('VOICE_NAME')

# Initialize APIs
client = OpenAI(api_key=OPENAI_API_KEY)
gmaps = googlemaps.Client(key=GOOGLE_API)

# Set Startup Variables
global files_array
global vector_store_id
global listening
speech = False
speech_file = "output.mp3"
listening = False
hotkeys = True
files_array = []
vector_store_id = ""

# Load Functions File
with open(tools, "r") as toollist_file:
    toollist = json.load(toollist_file)

pygame.mixer.init()
speech_array = []

recognizer = sr.Recognizer()

# Function Definitions
def get_coords(): # Gets Latitude and Longitude of user
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
        print(system_color + f"System: Latitude: {lat}, Longitude: {long}")
        return f"Latitude: {lat}, Longitude: {long}"
    else:
        print(system_color + f"System: System: Could not determine the latitude and longitude.")
        return "Could not determine the latitude and longitude."

def get_current_city(): # Gets the city of the user's current location
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lat' in geolocation_result['location'] and 'lng' in geolocation_result['location']:
        lat = geolocation_result['location']['lat']
        long = geolocation_result['location']['lng']
    else:
        print(system_color + f"System: System: Could not determine the latitude and longitude.")
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
        print(Fore.MAGENTA + f"System: System: Could not determine the latitude and longitude.")
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
        print(Fore.MAGENTA + f"System: System: Could not determine the latitude and longitude.")
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
        print(Fore.MAGENTA + f"System: System: Could not determine latitude.")
        return "Could not determine latitude."
    
def get_longitude(): # Gets the user's current longitude
    geolocation_result = gmaps.geolocate()
    if 'location' in geolocation_result and 'lng' in geolocation_result['location']:
        long = geolocation_result['location']['lng']
        return long
    else:
        print(Fore.MAGENTA + f"System: System: Could not determine the longitude.")
        return "Could not determine the longitude."

def new_note(note_to_add): # Writes a new line to the notes file
    try:
        notes = open(notes_file, "a")
        notes.write(note_to_add)
        print(Fore.MAGENTA + f"System: {note_to_add} succesfully appended to note file")
        notes.close()
    except Exception as e:
        print(Fore.MAGENTA + f"System: Failed to append note to note file. Reason:{e}")
        return f"Failed to append note to note file. Reason:{e}"

def overwrite_note(note_to_replace): # Overwrites the notes file
    try:
        notes = open(notes_file, "w")
        notes.write(note_to_replace)
        print(Fore.MAGENTA + f"System: Succesfully overwrote notes with {note_to_replace}")
        notes.close()
    except Exception as e:
        print(Fore.MAGENTA + f"System: Failed to overwrite note file. Reason:{e}")
        return f"Failed to overwrite note file. Reason:{e}"

def commit_memory(memory_to_commit): # Writes a new line to the memory file
    try:
        memories = open(memories_file, "a")
        memories.write(memory_to_commit)
        print(Fore.MAGENTA + f"System: {memory_to_commit} succesfully commited to memory")
        memories.close()
    except Exception as e:
        print(Fore.MAGENTA + f"System: Failed to commit {memory_to_commit} to long term memory. Reason:{e}")
        return f"Failed to commit {memory_to_commit} to long term memory. Reason:{e}"

def overwrite_memory(new_memory): # Overwrites memory file
    try:
        memories = open(memories_file, "w")
        memories.write(new_memory)
        print(Fore.MAGENTA + f"System: Succesfully overwrote memory with {new_memory}")
        memories.close()
    except Exception as e:
        print(Fore.MAGENTA + f"System: Failed to overwrite memory file. Reason:{e}")
        return f"Failed to overwrite memory file. Reason:{e}"

def cls(): # Function for clearing the screen
    os.system('cls' if os.name=='nt' else 'clear')

def speak():
    global speech_array
    joined_text = ''.join(speech_array)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice_model,
        input=joined_text,
    )
    response.stream_to_file(speech_file)
    global speech_output
    speech_output = pygame.mixer.Sound(speech_file)
    pygame.mixer.Sound.play(speech_output)
    speech_array = []
    sleep(pygame.mixer.Sound.get_length(speech_output))

def stop_speech():
    try:
        pygame.mixer.Sound.stop(speech_output)
        print(Fore.MAGENTA + f"System: Speech Halted")
    except:
        print(Fore.MAGENTA + "System: No Speech Process Running")

def calibrate_mic():
    # Use the default microphone as the audio source
    try:
        with sr.Microphone() as source:
            print(Fore.MAGENTA + "System: Please wait. Calibrating microphone...")
            # Listen for 2 seconds and calibrate the energy threshold for ambient noise levels
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print(Fore.MAGENTA + "System: Microphone calibrated, please speak.")
    except Exception as e:
        print(Fore.MAGENTA + f"System: {e}")
        
def recognize_speech_from_mic():
    # Use the default microphone as the audio source
    try:
        with sr.Microphone() as source:
            
            # Listen for the user's input (the first phrase detected)
            audio = recognizer.listen(source)
    except:
        print(Fore.RED + "No Microphone Detected")
        audio = None
    
    try:
        if audio is not None:
            # Using google speech recognition
            print(Fore.MAGENTA + "System: Recognizing speech...")
            text = recognizer.recognize_google(audio)
            print(Fore.GREEN + f"User: {text}")
            return text
        else:
            print(Fore.RED + "No Microphone Detected")

    except sr.UnknownValueError:
        print(Fore.MAGENTA + "System: Google Speech Recognition could not understand audio")
        return None

    except sr.RequestError as e:
        print(Fore.MAGENTA + "System: Could not request results from Google Speech Recognition service; {e}")
        return None

def toggle_listening():
    global listening
    listening = not listening
    print(Fore.MAGENTA + f"System: Conversational Mode Set To {listening}")
    sleep(0.5)

def toggle_speech():
    global speech
    speech = not speech
    state = "Enabled" if speech else "Disabled"
    print(Fore.MAGENTA + f"System: Speech {state}")
    sleep(0.5)

def toggle_hotkeys():
    global hotkeys
    if hotkeys:
        hotkeys = False
        keyboard.unhook_all()
    else:
        hotkeys = True
        keyboard.add_hotkey('q', toggle_listening)
        keyboard.add_hotkey('space', toggle_speech)
        keyboard.add_hotkey('x', stop_speech)
        
def del_ass(assid):
    client.beta.assistants.delete(assid)
    print(Fore.MAGENTA + f"System: Deleted Assistant with ID {assid} from OpenAI Servers")
    
cls()

# Assemble The Voice Assistant
try:
    vassistant = client.beta.assistants.create(
        instructions = vinstructions,
        name = vname,
        model = vmodel_name,
        tools = toollist
    )
    print(Fore.MAGENTA + f"System: Voice Assistant Assembled with ID {vassistant.id}")
except Exception as e:
    print(Fore.RED + f"Failed to retrieve OpenAI Assistant: {e}")
# Assemble the Text Assistant
try:
    assistant = client.beta.assistants.create(
        instructions = instructions,
        name = name,
        model = model_name,
        tools = toollist
    )
    print(Fore.MAGENTA + f"System: Text Assistant Assembled with ID {assistant.id}")
except Exception as e:
    print(Fore.RED + f"Failed to retrieve OpenAI Assistant: {e}")

# Create an EventHandler class to handle assistant responses and function calls
class EventHandler(AssistantEventHandler):
  # Handle new text generated
  def on_text_delta(self, delta, snapshot):
    print(Fore.CYAN + f"{delta.value}", end="", flush=True)
    loggerfunc.log(f"{delta.value}", thread_id)
    if speech == 1:
        speech_array.append(delta.value)
  # Handle assistant call for function
  def on_tool_call_created(self, tool_call):
    print(Fore.MAGENTA + f"\nassistant > {tool_call.type}\n", flush=True)
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
      print(Fore.CYAN + "Assistant: ", end="", flush=True)
      loggerfunc.log("Assistant: ", thread_id)
  # Function Call Handler
  def handle_requires_action(self, data, run_id):
    tool_outputs = []
     
    for tool in data.required_action.submit_tool_outputs.tool_calls:
      
      print(Fore.MAGENTA + f"Tool Name: {json.dumps(tool.function.name)}") # Debugging printout
      print(Fore.MAGENTA + f"Tool Arguments:{json.dumps(tool.function.arguments)}") # Debugging printout
      loggerfunc.newline(thread_id)
      loggerfunc.log("TOOL CALL", thread_id)
      loggerfunc.newline_no_dash(thread_id)
      loggerfunc.log(f"Tool Name: {json.dumps(tool.function.name)}", thread_id)
      loggerfunc.newline_no_dash(thread_id)
      
      # Split tool call into tool name and arguments provided
      arguments = json.loads(tool.function.arguments) if isinstance(tool.function.arguments, str) else tool.function.arguments
      
      print(Fore.MAGENTA + f"Parsed Arguments:{arguments}") # Debugging printout
      loggerfunc.log(f"Parsed Arguments:{arguments}", thread_id)
      loggerfunc.newline(thread_id)
      print(Fore.WHITE + "----------------------------------------------------------------------------------------")
      
      if tool.function.name == "get_time":
        # Parse arguments into internal variable
        timezone_str = arguments.get("time_zone", "UTC")
        time_format = arguments.get("format", "12hr")
        
        try:
          timezone = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
          tool_outputs.append({"tool_call_id": tool.id, "output": "Timezone unrecognized. Please use a timezone in the pytz python library. e.g. America/New York"})
        
        now = datetime.now(timezone)
        
        if time_format == "12hr":
          current_time = now.strftime('%I:%M%p')
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
            print(Fore.MAGENTA + f"System: Timestep accepted. Getting daily forecast.")
        elif timestep == "hourly":
            query_timestep = "1h"
            print(Fore.MAGENTA + f"System: Timestep accepted. Getting hourly forecast.")
        else:
            query_timestep = "1d"
            print(Fore.MAGENTA + f"System: Timestep is invalid. Defaulting to daily forecast.")
            
        # Parse Unit variable for API call
        if unit == "f":
            query_unit = "imperial"
            print(Fore.MAGENTA + f"System: Unit type accepted. Using Imperial system.")
        elif unit == "c":
            query_unit = "metric"
            print(Fore.MAGENTA + f"System: Unit type accepted. Using Metric system.")
        else:
            query_unit = "imperial"
            print(Fore.MAGENTA + f"System: Unit type is invalid. Defaulting to Imperial units.")
        
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
        print(Fore.MAGENTA + f"System: Tool Call Was Invalid") # Debugging printout
    
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
    calibrate_mic()
    # Start Main Thread
    try:
        global thread_id
        thread = client.beta.threads.create()
        thread_id = thread.id
        print(Fore.MAGENTA + f"System: Created New Thread with ID: {thread.id}")
        print(Fore.WHITE + "Type '?' for help.")
    except Exception as e:
        print(Fore.MAGENTA + f"System: Failed to create thread: {e}")
        return
    
    # Start Main Loop
    while True:
        # Set Variables and formatting
        global vector_store_id, files_array
        if listening:
            print(Fore.WHITE + f"Assistant ID: {vassistant.id} - Thread ID: {thread_id}")
        else:
            print(Fore.WHITE + f"Assistant ID: {assistant.id} - Thread ID: {thread_id}")
        print(Fore.WHITE + "-------------------------------------------------------------------------------------------")
        user_data = f"<Location: {get_current_location()} Latitude:{get_latitude()} Longitude:{get_longitude()}><Device:{get_device_info()}><Query Time:{get_current_time()}>" # User data part of query
        
        if listening:
            if hotkeys is False:
                toggle_hotkeys()
            print(Fore.WHITE + "Press 'q' to stop listening. Press 'Space' to toggle speech. Press 'x' to stop TTS response")
            user_input = recognize_speech_from_mic()
        else:
            if hotkeys:
                toggle_hotkeys()
            user_input = input(Fore.GREEN + "User: ")
            # Split command or user query into individual words
            command_parts = user_input.split()
            command = command_parts[0].lower()
            arg1 = command_parts[1] if len(command_parts) > 1 else None
            arg2 = ' '.join(command_parts[2:])
            if command in ["exit", "quit"]: # Exit Command
                print(Fore.MAGENTA + f"System: Starting cleanup process")
                try:
                    if files_array is not None:
                        for x in files_array:
                            try:
                                client.files.delete(x)
                                print(Fore.MAGENTA + f"System: Deleted File with ID: {x}")
                            except Exception as e:
                                print(Fore.RED + f"Failed to Delete File with ID: {x} Reason: {e}")
                except:
                    print(Fore.MAGENTA + "System: No Files Uploaded or Array Was Initialized Improperly.")
                try:
                    if vector_store_id != "":
                        try:
                            client.beta.vector_stores.delete(vector_store_id=f"{vector_store_id}")
                            print(Fore.MAGENTA + f"System: Deleted Vector Store with ID: {vector_store_id}")
                        except Exception as e:
                            print(Fore.RED + f"Failed to Delete Vector Store with ID {vector_store_id} Reason: {e}")
                except:
                    print(Fore.RED + "System: No Vector Store Initalized")
                try:
                    del_ass(assistant.id)
                    del_ass(vassistant.id)
                except Exception as e:
                    print(Fore.RED + f"Failed to Delete Assistant Configuration from OpenAI. Reason: {e}")
                print(Fore.MAGENTA + f"System: Cleanup complete. Ending chat.")
                print(Fore.WHITE)
                break
            elif command == "retrieve" and arg1: # Thread Retrieval Command
                try:
                    thread = client.beta.threads.retrieve(thread_id=arg1)
                    thread_id = thread.id
                    print(Fore.MAGENTA + f"System: Detached from old thread and attached to thread with ID: {thread.id}")
                except Exception as e:
                    print(Fore.RED + f"Failed to retrieve thread: {e}")
                    print(Fore.MAGENTA + f"System: Attaching to old thread with ID: {thread.id}")    
                continue
            elif command == "retrieve" and arg1 is None: # Handle retrieve usage if no arguments given
                print(Fore.MAGENTA + f"System: No Thread ID Provided")
                continue
            elif command in ["clear"]: # Clear Thread Command
                cls()
                print(Fore.MAGENTA + f"System: Closing current thread({thread_id}) and creating new one")
                try:
                    thread = client.beta.threads.create()
                    thread_id = thread.id
                    print(Fore.MAGENTA + f"System: Created New Thread with ID: {thread.id}")
                except Exception as e:
                    print(Fore.RED + f"Failed to create thread: {e}")
                    return
                continue
            elif command in ["cls"]:
                cls()
                print(Fore.MAGENTA + f"System: Cleared Screen. Current Thread ID:{thread.id}")
                continue
            elif command in ["stop", "shut"]:
                stop_speech()
                continue
            elif command == "upload" and arg1 and arg2:
                try:
                    file = client.files.create(
                        file=Path(arg1),
                        purpose='assistants'
                    )
                    # Create array to store file IDs
                    files_array = [f"{file.id}"]  # This should be a simple list of strings
                    print(Fore.MAGENTA + f"System: File Uploaded to OpenAI Assistant Successfully with ID: {file.id}")
                    # Create Vector Store and attach File ID
                    vector_store = client.beta.vector_stores.create(
                        name=f"Vector Store for Thread ID: {thread.id}",
                        file_ids=files_array,  # Passing simple list
                        expires_after={
                            "anchor": "last_active_at",
                            "days": 1
                        },
                    )
                    vector_store_id = vector_store.id
                    print(Fore.MAGENTA + f"System: Vector Store Created Succesfully with ID: {vector_store.id}")
                    try:
                        client.beta.threads.update(
                            thread_id,
                            tool_resources={
                                "file_search": {
                                    "vector_store_ids": [vector_store.id], 
                                }
                            }
                        )
                        print(Fore.MAGENTA + f"System: Vector Store with ID {vector_store.id} Attached Succesfully to Thread with ID {thread.id}")
                    except Exception as e:
                        print(Fore.MAGENTA + f"System: Vector Store Failed to Attach to Thread ID: {thread_id} for reason: {e}")
                    
                    client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=f"{arg2} `User Data: {user_data}`"
                    )
                    print(" ")
                    print(Fore.WHITE + "----------------------------------------------------------------------------------------")
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
                continue
            elif command == "upload" and arg1 is None:
                print(Fore.MAGENTA + f"System: System: No file provided.")
                continue
            elif command == "upload" and arg2 is None:
                print(Fore.MAGENTA + f"System: System: No query provided.")
                continue
            elif command == "speech":
                toggle_speech()
                continue
            elif command == "listen":
                toggle_listening()
                continue
            elif command == "ids":
                print(Fore.WHITE + f"Text Assistant ID: {assistant.id}")
                print(Fore.WHITE + f"Voice Assistant ID: {vassistant.id}")
                print(Fore.WHITE + f"Thread ID: {thread.id}")
                if vector_store_id is not None:
                    print(Fore.WHITE + f"Vector Store ID: {vector_store_id}")
                if files_array is not None:
                    print(Fore.WHITE + f"File IDs: {files_array}")
                continue
            elif command in ["help", "?"]: # Help Command
                print(Fore.MAGENTA + "System: Displaying Help Message...")
                print(Back.WHITE + Fore.MAGENTA + "Message Meaning:                                                                           ")
                print(Fore.MAGENTA + "System:" + Fore.BLACK + " This is a system message. Only really useful for debugging or general info.        ")
                print(Fore.CYAN + "Assistant:" + Fore.BLACK + " This is a response from your assistant.                                         ")
                print(Fore.GREEN + "User:" + Fore.BLACK + " This is a user query.                                                                ")
                print(Fore.RED + "Anything in red is an error.                                                               ")
                print(Fore.BLACK + "-------------------------------------------------------------------------------------------")
                print(Fore.MAGENTA + "Commands:                                                                                  ")
                print(Fore.BLACK + "help/?                - lists this dialog                                                  ")
                print("clear                 - deletes the current thread and creates a new one                   ")
                print("cls                   - clears the screen but keeps thread attachment                      ")
                print("retrieve (Thread ID)  - attaches to a predefined thread ID                                 ")
                print("upload (File) (Query) - Uploads a file to the assistant for it to analyze                  ")
                print("speech                - Toggles TTS Responses                                              ")
                print("listen                - Toggles conversational mode                                        ")
                print("stop                  - Stops current running TTS Response                                 ")
                print("ids                   - Lists IDs related to your conversation                             ")
                print("exit                  - closes the program                                                 ")
                print(Back.BLACK + Fore.WHITE)
                continue
        if user_input:
            try:
                loggerfunc.log(f"User: {user_input}", thread_id)
                loggerfunc.newline(thread_id)
                    
                # Add the user message to the thread
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"{user_input} `User Data: {user_data}`"
                )
                print(" ")
                print(Fore.WHITE + "----------------------------------------------------------------------------------------")
                    
                # Create new EventHandler instance for each stream
                event_handler = EventHandler()
                    
                # Stream the assistant's response
                if listening:
                    with client.beta.threads.runs.stream(
                        thread_id=thread.id,
                        assistant_id=vassistant.id,
                        event_handler=event_handler
                    ) as stream:
                        stream.until_done()
                        print("")
                        if speech == True:
                            print(Fore.MAGENTA + "Generating Speech Output...")
                            print(Fore.WHITE)
                            speak()
                else:
                    with client.beta.threads.runs.stream(
                        thread_id=thread.id,
                        assistant_id=assistant.id,
                        event_handler=event_handler
                    ) as stream:
                        stream.until_done()
                        print("")
                        if speech == True:
                            print(Fore.MAGENTA + "Generating Speech Output...")
                            print(Fore.WHITE)
                            speak()
            except Exception as e:
                print(Fore.MAGENTA + "System: Error loading user input. Reason: {e}")


# Start main loop
if __name__ == "__main__":
    run_assistant()