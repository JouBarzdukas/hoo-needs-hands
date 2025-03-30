import asyncio
import aiofiles
import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

app = FastAPI()

def process_line(line: str):
    """
    Process each line of the file. If processing produces a string, return it.
    Otherwise, return None to do nothing.
    """
    line = line.strip()
    if line:  # Example logic: only send non-empty lines
        return f"Processed: {line}"
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