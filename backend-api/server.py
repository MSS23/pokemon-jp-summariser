from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
import re
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
import base64

app = FastAPI(title="Pokemon Translation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Initialize Gemini model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1,
    max_tokens=8192
)

# Request/Response models
class ArticleRequest(BaseModel):
    url: Optional[str] = None
    direct_text: Optional[str] = None

class PokemonTeam(BaseModel):
    name: str
    ability: str
    item: str
    tera_type: str
    nature: str
    moves: List[str]
    evs: dict
    ev_spread: str
    ev_explanation: str

class AnalysisResponse(BaseModel):
    title: str
    summary: str
    teams: List[PokemonTeam]
    strengths: List[str]
    weaknesses: List[str]
    success: bool
    error: Optional[str] = None

# Rate limiting (simple in-memory implementation)
import time
from collections import defaultdict

request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting implementation"""
    current_time = time.time()
    # Remove old requests outside the window
    request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                if current_time - req_time < RATE_LIMIT_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False
    
    request_counts[client_ip].append(current_time)
    return True

# Utility functions (same as your current implementation)
async def fetch_article_content(url: str) -> tuple[str, List[str]]:
    """Fetch article content and extract images"""
    # Implementation from your current geminiService.ts
    # This would be the same logic you have in the React app
    pass

def parse_detailed_team_members(llm_output: str) -> List[dict]:
    """Parse LLM output to extract Pokemon details"""
    # Implementation from your current geminiService.ts
    pass

def parse_ev_spread(ev_text: str) -> dict:
    """Parse EV spread text to structured data"""
    # Implementation from your current geminiService.ts
    pass

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_article(request: ArticleRequest, client_ip: str = "unknown"):
    """Analyze a Pokemon article and extract team information"""
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        # Validate input
        if not request.url and not request.direct_text:
            raise HTTPException(status_code=400, detail="Either URL or direct_text must be provided")
        
        # Fetch content
        if request.url:
            article_text, images = await fetch_article_content(request.url)
        else:
            article_text = request.direct_text
            images = []
        
        # Prepare prompt (same as your current implementation)
        prompt_template = """
        [Your existing prompt template from utils/llm_summary.py]
        """
        
        # Create messages for Gemini
        messages = []
        
        # Add text content
        messages.append(HumanMessage(content=f"{prompt_template}\n\nArticle Content:\n{article_text}"))
        
        # Add images if available
        for image_url in images[:4]:  # Limit to 4 images
            try:
                # Convert image to base64
                # Implementation here
                pass
            except Exception as e:
                print(f"Failed to process image {image_url}: {e}")
        
        # Call Gemini API
        response = await model.ainvoke(messages)
        
        # Parse response
        parsed_data = parse_detailed_team_members(response.content)
        
        # Extract strengths and weaknesses
        # Implementation here
        
        return AnalysisResponse(
            title=parsed_data.get('title', 'Unknown'),
            summary=parsed_data.get('summary', ''),
            teams=parsed_data.get('pokemon', []),
            strengths=parsed_data.get('strengths', []),
            weaknesses=parsed_data.get('weaknesses', []),
            success=True
        )
        
    except Exception as e:
        return AnalysisResponse(
            title="",
            summary="",
            teams=[],
            strengths=[],
            weaknesses=[],
            success=False,
            error=str(e)
        )

@app.get("/api/usage/{client_ip}")
async def get_usage_stats(client_ip: str):
    """Get usage statistics for a client (for monitoring)"""
    current_time = time.time()
    recent_requests = [req_time for req_time in request_counts[client_ip] 
                      if current_time - req_time < RATE_LIMIT_WINDOW]
    
    return {
        "client_ip": client_ip,
        "requests_in_window": len(recent_requests),
        "rate_limit": RATE_LIMIT,
        "window_seconds": RATE_LIMIT_WINDOW
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 