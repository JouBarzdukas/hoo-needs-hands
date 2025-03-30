import asyncio
import aiofiles
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import re

app = FastAPI()

def process_line(line: str):
    """
    Process each line of the file based on predefined rules.
    """
    line = line.strip()
    if not line:
        return None

    # if "Wake word 'Jarvis' detected. Starting recording." in line:
    #     return "mic-on"
    # elif "Recording... Speak now." in line:
    #     return "mic-on"
    # elif line.startswith("Segment"):
    #     match = re.search(r"Segment \d+: (.+)", line)
    #     if match:
    #         return f"🗣️ {match.group(1).strip()}"
    # elif "Waiting for confirmation..." in line:
    #     return "mic-on"
    # elif "Stop keyword 'blueberry' detected." in line or line.starswith("Confirmation response:"):
    #     return "mic-off"
    # elif line.startswith("INFO     [agent] 🚀 Starting task:"):
    #     return f"Browser Agent Starting Task: {line.split('Starting task:')[1].strip()}"
    # elif line.startswith("INFO     [controller]"):
    #     return f"Browser Agent Executed: {line.split('INFO     [controller]')[1].strip()}"
    # elif "INFO     [agent] ✅ Task completed" in line:
    #     return "Browser Agent: Completed Task"
    
    match line:
        case line if "Wake word 'Jarvis' detected. Starting recording." in line:
            return "mic-on"
        # case line if "Recording... Speak now." in line:
        #     return "mic-on"
        case line if line.startswith("Segment"):
            if match := re.search(r"Segment \d+: (.+)", line):
                return f"🗣️ {match.group(1).strip()}"
        case line if "Waiting for confirmation..." in line:
            return "mic-on"
        case line if "Stop keyword 'blueberry' detected." in line or line.startswith("Confirmation response:"):
            return "mic-off"
        case line if line.startswith("INFO     [agent] 🚀 Starting task:"):
            return f"Browser Agent Starting Task: {line.split('Starting task:')[1].strip()}"
        case line if line.startswith("INFO     [controller]"):
            return f"Browser Agent Executed: {line.split('INFO     [controller]')[1].strip()}"
        case line if "INFO     [agent] ✅ Task completed" in line:
            return "Browser Agent: Completed Task"
    
    return None
    
async def watch_file(file_path: str) -> AsyncGenerator[str, None]:
    """Watches a file for new lines and processes them."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    async with aiofiles.open(file_path, mode='r') as file:
        await file.seek(0, os.SEEK_END)  # Move to the end of the file
        while True:
            line = await file.readline()
            if not line:
                await asyncio.sleep(0.5)  # Wait before checking again
                continue
            result = process_line(line)
            if result:
                yield f"data: {result}\n\n"

@app.get("/stream")
async def stream(file_path: str = "/Users/pradeepravi/Documents/hoo-needs-hands/backend/output.txt"):
    """Endpoint to stream processed file changes via SSE."""
    return StreamingResponse(watch_file(file_path), media_type="text/event-stream")

# create main if statemnt
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )