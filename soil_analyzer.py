import google.generativeai as genai
from PIL import Image
import logging
import json
import os

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDkrgEPkgxdY_lz9tLJ8c6eAKCnsFyUCJ0')

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
You are an expert agricultural soil scientist with image recognition capabilities.

FIRST, determine if this image shows SOIL or something else.

If this is SOIL, analyze it and provide:
{
  "is_soil": true,
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

If this is NOT SOIL, identify what it is and respond:
{
  "is_soil": false,
  "detected_object": "What you see (e.g., floor tiles, fabric, wood, concrete, food, person, animal, etc.)",
  "message": "This image shows [object], not soil. Please upload a clear photo of soil for analysis.",
  "tips": [
    "Take a photo of actual ground soil",
    "Ensure good lighting",
    "Remove any debris or objects",
    "Focus on the soil surface"
  ]
}

ANALYSIS RULES FOR SOIL:
1. Color Analysis:
   - Dark brown/black = High organic matter
   - Red/Orange = Iron oxide (Fe₂O₃) present
   - Yellow = Hydrated iron, moderate fertility
   - Gray/White = Sandy, leached, low nutrients
   
2. Texture Analysis:
   - Fine particles = Clay soil (high water retention)
   - Coarse particles = Sandy soil (good drainage)
   - Mixed = Loamy soil (ideal for farming)
   
3. pH Estimation:
   - Clay/dark soils = 6.0-7.0
   - Sandy/light soils = 5.0-6.0
   - Loamy soils = 6.5-7.0
   
4. Give specific, actionable recommendations

Respond with ONLY valid JSON.
"""
            
            response = self.model.generate_content([prompt, image])
            
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                return self._fallback_analysis()
            
            logger.info(f"📥 Gemini soil analysis: {response.text[:200]}...")
            
            result = self._parse_response(response.text)
            
            if result.get('is_soil', True):
                logger.info(f"🌱 Soil Type: {result['soil_type']}, pH: {result['ph_estimate']}")
            else:
                logger.info(f"❌ Not soil - Detected: {result.get('detected_object', 'Unknown object')}")
            
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
            
            # Check if it's soil or not
            is_soil = data.get('is_soil', True)
            
            if not is_soil:
                # Return non-soil response - NO ph_estimate parsing needed!
                logger.info(f"🚫 Not soil detected: {data.get('detected_object', 'Unknown')}")
                return {
                    "success": False,
                    "is_soil": False,
                    "detected_object": data.get('detected_object', 'Unknown object'),
                    "message": data.get('message', 'This does not appear to be soil. Please upload a soil image.'),
                    "tips": data.get('tips', [
                        "Take a photo of actual ground soil",
                        "Ensure good lighting",
                        "Remove any debris or objects",
                        "Focus on the soil surface"
                    ]),
                    "soil_type": "Not Soil",
                    "color": "N/A",
                    "texture": "N/A",
                    "moisture": "N/A",
                    "ph_estimate": 0,
                    "nitrogen": "N/A",
                    "phosphorus": "N/A",
                    "potassium": "N/A",
                    "organic_matter": "N/A",
                    "recommendations": "Please upload a valid soil image for analysis.",
                    "suitable_crops": [],
                    "improvements": "N/A"
                }
            
            # Return soil analysis - parse ph_estimate safely
            ph_value = data.get('ph_estimate', 6.5)
            try:
                ph_value = float(ph_value) if ph_value is not None else 6.5
            except (ValueError, TypeError):
                ph_value = 6.5
            
            return {
                "success": True,
                "is_soil": True,
                "soil_type": data.get('soil_type', 'Unknown'),
                "color": data.get('color', 'Not determined'),
                "texture": data.get('texture', 'Medium'),
                "moisture": data.get('moisture', 'Unknown'),
                "ph_estimate": ph_value,
                "nitrogen": data.get('nitrogen', 'Medium'),
                "phosphorus": data.get('phosphorus', 'Medium'),
                "potassium": data.get('potassium', 'Medium'),
                "organic_matter": data.get('organic_matter', 'Medium'),
                "recommendations": data.get('recommendations', 'Consult local agricultural expert'),
                "suitable_crops": data.get('suitable_crops', ['Rice', 'Wheat', 'Vegetables']),
                "improvements": data.get('improvements', 'Add organic compost')
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._fallback_analysis()
        except Exception as e:
            logger.error(f"Failed to parse soil response: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self):
        return {
            "success": False,
            "is_soil": True,
            "soil_type": "Analysis Unavailable",
            "color": "Unknown",
            "texture": "Unknown",
            "moisture": "Unknown",
            "ph_estimate": 6.5,
            "nitrogen": "Medium",
            "phosphorus": "Medium",
            "potassium": "Medium",
            "organic_matter": "Medium",
            "recommendations": "AI service temporarily unavailable. Please try again.",
            "suitable_crops": [],
            "improvements": "Please try again later"
        }

soil_analyzer = SoilAnalyzer()
