from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io
import logging

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)

# Import AI models
from disease_model import detector
from soil_analyzer import soil_analyzer
from chatbot import chatbot

app = FastAPI(title="AgriSmart ML Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    userName: str = "Farmer"

@app.get("/")
async def root():
    return {
        "service": "AgriSmart ML Service",
        "status": "running",
        "version": "2.0",
        "ai": "Google Gemini Vision",
        "features": ["Disease Detection", "Soil Analysis", "AI Chatbot"],
        "endpoints": {
            "disease_detection": "/api/disease-detection",
            "soil_analysis": "/api/soil-analysis",
            "chat": "/api/chat"
        }
    }

@app.post("/api/disease-detection")
async def analyze_disease(image: UploadFile = File(...)):
    try:
        logger.info("="*60)
        logger.info("📸 DISEASE DETECTION REQUEST")
        
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        logger.info(f"📊 Image: {img.size}, Mode: {img.mode}")
        
        result = detector.analyze_disease(img)
        
        logger.info(f"🎯 Result: {result['disease']} ({result['confidence']*100:.1f}%)")
        logger.info("="*60)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {
            "success": False,
            "disease": "Processing Error",
            "confidence": 0.0,
            "severity": "Error",
            "description": str(e),
            "treatment": "Please try again",
            "prevention": "Ensure image is valid"
        }

@app.post("/api/soil-analysis")
async def analyze_soil(image: UploadFile = File(...)):
    try:
        logger.info("="*60)
        logger.info("🌱 SOIL ANALYSIS REQUEST")
        
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        logger.info(f"📊 Image: {img.size}, Mode: {img.mode}")
        
        result = soil_analyzer.analyze_soil(img)
        
        logger.info(f"🌱 Soil: {result['soil_type']}, pH: {result['ph_estimate']}")
        logger.info("="*60)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {
            "success": False,
            "soil_type": "Processing Error",
            "color": "Unknown",
            "texture": "Unknown",
            "moisture": "Unknown",
            "ph_estimate": 6.5,
            "nitrogen": "Unknown",
            "phosphorus": "Unknown",
            "potassium": "Unknown",
            "organic_matter": "Unknown",
            "recommendations": "Error processing image",
            "suitable_crops": [],
            "improvements": "Please try again"
        }

@app.post("/api/chat")
async def chat(message: ChatMessage):
    try:
        logger.info("="*60)
        logger.info(f"💬 CHAT REQUEST from {message.userName}: {message.message[:50]}...")
        
        result = chatbot.get_response(message.message, message.userName)
        
        logger.info(f"🤖 Response: {result['reply'][:50]}...")
        logger.info("="*60)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Chat Error: {e}")
        return {
            "reply": "I'm sorry, I'm having trouble responding right now. Please try again!",
            "success": False
        }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🤖 AgriSmart ML Service - ADVANCED AI")
    print("="*60)
    print("✨ Features:")
    print("  • Plant Disease Detection (Gemini AI)")
    print("  • Soil Analysis (Gemini AI)")
    print("  • AI Chatbot (Gemini AI)")
    print("="*60)
    print("📡 Port: 8000")
    print("🌐 Docs: http://localhost:8000/docs")
    print("="*60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
