"""
FastAPI server for Glock pk ai
"""

import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from glock_pk_ai.config import get_config
from glock_pk_ai.core.openai_client import OpenAIClient
from glock_pk_ai.core.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)
config = get_config()

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="An AI similar to Gemini powered by OpenAI"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ai_client = OpenAIClient()
conversation_manager = ConversationManager()


# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    conversation_id: Optional[str] = None


class CodeAnalysisRequest(BaseModel):
    code: str
    query: str
    conversation_id: Optional[str] = None


class FileProcessingRequest(BaseModel):
    content: str
    query: str
    file_type: str = "text"


class ChatMessage(BaseModel):
    role: str
    content: str


class ConversationResponse(BaseModel):
    conversation_id: str
    message: str


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": config.APP_NAME}


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    """Generate text using OpenAI"""
    try:
        conversation_id = request.conversation_id or conversation_manager.create_conversation()
        
        # Get conversation history
        history = conversation_manager.get_formatted_history(conversation_id, last_n=10)
        
        # Generate response
        response = await ai_client.generate_text(
            prompt=request.prompt,
            conversation_history=history if history else None,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
        )
        
        # Store in conversation history
        conversation_manager.add_message(conversation_id, "user", request.prompt)
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        return {
            "conversation_id": conversation_id,
            "prompt": request.prompt,
            "response": response,
        }
    
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-code")
async def generate_code(request: CodeGenerationRequest):
    """Generate code using OpenAI"""
    try:
        conversation_id = request.conversation_id or conversation_manager.create_conversation()
        
        # Get conversation history
        history = conversation_manager.get_formatted_history(conversation_id, last_n=10)
        
        # Generate code
        response = await ai_client.generate_code(
            prompt=request.prompt,
            language=request.language,
            conversation_history=history if history else None,
        )
        
        # Store in conversation history
        conversation_manager.add_message(conversation_id, "user", f"Generate {request.language} code: {request.prompt}")
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        return {
            "conversation_id": conversation_id,
            "language": request.language,
            "code": response,
        }
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-code")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code"""
    try:
        conversation_id = request.conversation_id or conversation_manager.create_conversation()
        
        # Get conversation history
        history = conversation_manager.get_formatted_history(conversation_id, last_n=10)
        
        # Analyze code
        response = await ai_client.analyze_code(
            code=request.code,
            query=request.query,
            conversation_history=history if history else None,
        )
        
        # Store in conversation history
        conversation_manager.add_message(conversation_id, "user", f"Analyze code: {request.query}")
        conversation_manager.add_message(conversation_id, "assistant", response)
        
        return {
            "conversation_id": conversation_id,
            "query": request.query,
            "analysis": response,
        }
    
    except Exception as e:
        logger.error(f"Error analyzing code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-file")
async def process_file(request: FileProcessingRequest):
    """Process file content"""
    try:
        response = await ai_client.process_file(
            file_content=request.content,
            query=request.query,
            file_type=request.file_type,
        )
        
        return {
            "query": request.query,
            "file_type": request.file_type,
            "result": response,
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation/{conversation_id}/message")
async def add_conversation_message(
    conversation_id: str,
    message: ChatMessage
):
    """Add message to conversation"""
    try:
        conversation_manager.add_message(
            conversation_id,
            message.role,
            message.content
        )
        
        return {
            "conversation_id": conversation_id,
            "message_added": True,
        }
    
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    try:
        history = conversation_manager.get_history(conversation_id)
        summary = conversation_manager.get_summary(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "summary": summary,
            "history": history,
        }
    
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation"""
    try:
        conversation_manager.delete_conversation(conversation_id)
        
        return {"conversation_id": conversation_id, "deleted": True}
    
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))