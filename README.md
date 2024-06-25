# CompanionPython
This program allows the user to define an OpenAI assistant and run it through OpenAI's python library.
I aimed to add as much functionality to it as possible and I tried my hardest to keep it multi-platform. This script comes with an assistant that has already been defined to use as an example or just as an assistant.

## **General Info**
This program has two operating modes. Conversational and textual. It uses two different assistants depending on the mode. This has been done mainly so that you can put in the instructions that the voice assistant should give responses more similar to human speech so the TTS responses have less artifacting when being given prompts.
- **Textual** - In textual mode the script runs just like any chat bot. You can query the assistant by just typing your query and pressing enter. However, there is a set of commands you can input that will not be sent as queries and is mainly for debugging or ease of use.
- **Conversational** - In conversational mode the assistant acts more like a voice assistant. You can talk to it and the script will use Google's speech recognition service to turn your speech into a query. TTS responses are optional.

### Commands
This program has a few commands the user can input while in textual mode to change how the program operates or change settings.
1. **help** - Displays a help dialog
2. **clear** - Detaches from the current thread and automatically generates a new one
3. **cls** - Clears the screen
4. **retrieve (Thread ID)** - Attaches to a pre-defined thread ID
5. **upload (filename) (query)** - Allows the user to upload a file and query the assistant
6. **speech** - Toggles TTS responses on and off
7. **listen** - Toggles conversational mode
8. **stop** - Stops any currently running TTS response
9. **ids** - Lists all IDs related to your conversation such as Thread ID, Assistant IDs, File IDs, and Vector Store IDs
10. **exit** - Closes the program
## **How to use**
This program has **2** files that are used when defining an assistant. 
- **1.** func.txt - Here you can define all of the tools/functions the assistant has access to. It comes with many preconfigured tools such as 'search' or 'get_time'
- **2.** .env - This is the configuration settings for the main script but has values related to assistant generation as well. Some important values here would be "INSTRUCTIONS" and "MODEL".

### **Set Up**
- Get an **OpenAI** API key
- Get a **Google** API key - ***Optional***
- Get a **ScaleSERP** API key - ***Optional***
- Get a **Tomorrow.IO** API key - ***Optional***
- Rename `RenameThisFile.env` to `.env`
- Place your API keys in the `.env` settings file
- Edit the 'func.txt' file - ***Optional***
- Edit the instructions in the `.env` file - ***Optional***
- Run `pip install -r requirements.txt` from within the program's folder
- Run `python RunCompanion.py`
