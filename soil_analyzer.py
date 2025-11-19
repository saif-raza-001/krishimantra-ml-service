import google.generativeai as genai
from PIL import Image
import logging
import json

logger = logging.getLogger(__name__)

GEMINI_API_KEY = "AIzaSyDkrgEPkgxdY_lz9tLJ8c6eAKCnsFyUCJ0"

class SoilAnalyzer:
    def __init__(self):
        logger.info("🌱 Initializing Soil Analysis AI...")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Soil Analyzer ready!")
        except Exception as e:
            logger.error(f"❌ Soil Analyzer initialization failed: {e}")
            self.model = None
    
    def analyze_soil(self, image):
        """
        Analyze soil image using Gemini AI
        """
        try:
            if not self.model:
                return self._fallback_analysis()
            
            logger.info("🔍 Analyzing soil with Gemini AI...")
            
            prompt = """
You are an expert agricultural soil scientist.

Analyze this soil image and provide a JSON response:

{
  "is_soil": true/false,
  "soil_type": "Clay/Loamy/Sandy/Silty/Peaty/Chalky",
  "color": "Description of soil color",
  "texture": "Fine/Medium/Coarse",
  "moisture": "Dry/Moist/Wet",
  "ph_estimate": 6.5,
  "nitrogen": "Low/Medium/High",
  "phosphorus": "Low/Medium/High",
  "potassium": "Low/Medium/High",
  "organic_matter": "Low/Medium/High",
  "recommendations": "Specific farming recommendations",
  "suitable_crops": ["Crop1", "Crop2", "Crop3"],
  "improvements": "How to improve this soil"
}

Rules:
1. If NOT soil (clothing, objects, people), set is_soil: false
2. Analyze color - dark = organic matter, red = iron, pale = sandy
3. Estimate texture from appearance
4. pH: Clay/dark (6-7), Sandy/light (5-6), Loamy (6.5-7)
5. Give specific crop recommendations
6. Provide actionable improvement advice

Respond with ONLY valid JSON.
"""
            
            response = self.model.generate_content([prompt, image])
            
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                return self._fallback_analysis()
            
            logger.info(f"📥 Gemini soil analysis: {response.text[:200]}...")
            
            result = self._parse_response(response.text)
            logger.info(f"🌱 Soil Type: {result['soil_type']}, pH: {result['ph_estimate']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Soil analysis error: {e}")
            return self._fallback_analysis()
    
    def _parse_response(self, response_text):
        try:
            json_text = response_text.strip()
            
            # Remove markdown
            if '```' in json_text:
                parts = json_text.split('```')
                for part in parts:
                    if part.strip().startswith('json'):
                        json_text = part.strip()[4:].strip()
                        break
                    elif part.strip().startswith('{'):
                        json_text = part.strip()
                        break
            
            data = json.loads(json_text.strip())
            
            return {
                "success": data.get('is_soil', True),
                "soil_type": data.get('soil_type', 'Unknown'),
                "color": data.get('color', 'Not determined'),
                "texture": data.get('texture', 'Medium'),
                "moisture": data.get('moisture', 'Unknown'),
                "ph_estimate": float(data.get('ph_estimate', 6.5)),
                "nitrogen": data.get('nitrogen', 'Medium'),
                "phosphorus": data.get('phosphorus', 'Medium'),
                "potassium": data.get('potassium', 'Medium'),
                "organic_matter": data.get('organic_matter', 'Medium'),
                "recommendations": data.get('recommendations', 'Consult local agricultural expert'),
                "suitable_crops": data.get('suitable_crops', ['Rice', 'Wheat', 'Vegetables']),
                "improvements": data.get('improvements', 'Add organic compost')
            }
            
        except Exception as e:
            logger.error(f"Failed to parse soil response: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self):
        return {
            "success": False,
            "soil_type": "Analysis Unavailable",
            "color": "Unknown",
            "texture": "Unknown",
            "moisture": "Unknown",
            "ph_estimate": 6.5,
            "nitrogen": "Medium",
            "phosphorus": "Medium",
            "potassium": "Medium",
            "organic_matter": "Medium",
            "recommendations": "AI service temporarily unavailable",
            "suitable_crops": [],
            "improvements": "Please try again"
        }

soil_analyzer = SoilAnalyzer()
