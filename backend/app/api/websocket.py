"""
WebSocket Handler - Real-time communication
"""

from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Set

from app.services.ollama import ollama_service
from app.services.debate import debate_service
from app.services.accuracy import accuracy_service
from app.models.schemas import PromptRequest, DebateRequest
from app.utils.logger import logger

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 WebSocket connected: {len(self.active_connections)} active")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"🔌 WebSocket disconnected: {len(self.active_connections)} active")
    
    async def send_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except:
            pass

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get('type', '')
            
            if msg_type == 'generate':
                # Stream generation
                prompt = data.get('prompt', '')
                system_prompt = data.get('system_prompt')
                settings = data.get('settings', {})
                
                await websocket.send_json({'type': 'start', 'message': 'Generating...'})
                
                try:
                    async for chunk in ollama_service.stream_generate(
                        prompt,
                        settings,
                        system_prompt
                    ):
                        await websocket.send_json({'type': 'chunk', 'content': chunk})
                    
                    await websocket.send_json({'type': 'done', 'message': 'Complete'})
                except Exception as e:
                    await websocket.send_json({'type': 'error', 'error': str(e)})
            
            elif msg_type == 'debate':
                # Start debate
                try:
                    debate_request = DebateRequest(**data.get('debate', {}))
                    result = await debate_service.conduct_debate(debate_request)
                    await websocket.send_json({
                        'type': 'debate_result',
                        'data': result.dict()
                    })
                except Exception as e:
                    await websocket.send_json({'type': 'error', 'error': str(e)})
            
            elif msg_type == 'ping':
                await websocket.send_json({'type': 'pong', 'timestamp': time.time()})
            
            elif msg_type == 'settings':
                # Update settings (only allows deterministic)
                await websocket.send_json({
                    'type': 'settings_update',
                    'temperature': 0.0,
                    'seed': 40,
                    'deterministic': True
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
