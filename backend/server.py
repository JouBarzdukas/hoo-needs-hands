from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Dict, List
from main import build_graph, State

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active conversations
active_conversations: Dict[str, List[Dict]] = {}

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    
    if conversation_id not in active_conversations:
        active_conversations[conversation_id] = []
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Add user message to conversation
            active_conversations[conversation_id].append({
                "role": "user",
                "content": message["content"]
            })
            
            # Process the command through the graph
            graph = build_graph()
            initial_state: State = {"messages": active_conversations[conversation_id]}
            
            # Send processing status
            await websocket.send_json({
                "type": "status",
                "content": "Processing command..."
            })
            
            # Process through graph
            for event in graph.stream(initial_state):
                if "messages" in event:
                    # Update conversation history
                    active_conversations[conversation_id] = event["messages"]
                    # Send the latest message
                    await websocket.send_json({
                        "type": "message",
                        "content": event["messages"][-1]["content"],
                        "role": event["messages"][-1]["role"]
                    })
            
            # Send completion status
            await websocket.send_json({
                "type": "status",
                "content": "Task completed"
            })
            
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
    finally:
        await websocket.close()

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    return active_conversations.get(conversation_id, [])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 