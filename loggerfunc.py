import re
from pathlib import Path

def remove_emojis(text):
    # This pattern identifies emojis
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def log(logtext, thread_id):
    logtext = remove_emojis(logtext)  # Remove emojis from logtext
    file = open(f"thread_log\\{thread_id}.txt", "a")
    file.write(f"{logtext}")
    file.close()

def newline(thread_id):
    file = open(f"thread_log\\{thread_id}.txt", "a")
    file.write("\n------------------------------------------------\n")
    file.close()
    
def newline_no_dash(thread_id):
    file = open(f"thread_log\\{thread_id}.txt", "a")
    file.write("\n")
    file.close()