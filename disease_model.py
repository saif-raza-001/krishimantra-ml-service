import google.generativeai as genai
from PIL import Image
import logging
import json
import io

logger = logging.getLogger(__name__)

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyDkrgEPkgxdY_lz9tLJ8c6eAKCnsFyUCJ0"

class PlantDiseaseDetector:
    def __init__(self):
        logger.info("🤖 Initializing Google Gemini Vision AI...")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Use the CORRECT model names from your available list
            model_names = [
                'gemini-2.5-flash',           # Latest stable
                'gemini-flash-latest',        # Always latest
                'gemini-2.0-flash',           # Stable alternative
            ]
            
            self.model = None
            
            for model_name in model_names:
                try:
                    logger.info(f"🔍 Trying model: {model_name}...")
                    self.model = genai.GenerativeModel(model_name)
                    logger.info(f"✅ Successfully using model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"❌ Model {model_name} failed: {e}")
                    continue
            
            if not self.model:
                raise Exception("No valid Gemini model found")
                
            logger.info("✅ Gemini AI initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            self.model = None
    
    def analyze_disease(self, image):
        """
        Use Google Gemini Vision to analyze plant diseases
        """
        try:
            if not self.model:
                logger.error("Model not initialized")
                return self._fallback_analysis()
            
            logger.info("🔍 Sending image to Google Gemini Vision AI...")
            
            # Prepare prompt for plant disease detection
            prompt = """
You are an expert agricultural AI assistant specializing in plant disease detection.

Analyze this image and provide a JSON response with the following structure:

{
  "is_plant": true/false,
  "disease": "Name of disease or 'Healthy' or 'Not a Plant'",
  "confidence": 0.0-1.0,
  "severity": "None/Low/Medium/High/Error",
  "description": "Brief description of the condition",
  "treatment": "Recommended treatment (or 'N/A' if not a plant)",
  "prevention": "Prevention measures (or 'N/A' if not a plant)"
}

Rules:
1. If the image does NOT contain a plant (e.g., clothing, objects, people, animals), set:
   - is_plant: false
   - disease: "Not a Plant Image"
   - severity: "Error"
   - description: "This image doesn't show plant vegetation"
   - treatment: "N/A"
   - prevention: "N/A"

2. If it's a plant, analyze for diseases:
   - Common diseases: Leaf Blight, Powdery Mildew, Rust, Bacterial Spot, Anthracnose, Downy Mildew, Leaf Spot, etc.
   - Consider: leaf color (yellow, brown, green), spots, wilting, discoloration, texture, holes
   - Yellow/brown/spotted leaves often indicate disease (NOT "not a plant")
   - Even unhealthy plants are still plants!

3. Be STRICT about rejecting non-plant images (clothing, furniture, people, food items, animals)
4. Be LENIENT with diseased/damaged plants - they're still plants!
5. Provide specific, actionable treatment recommendations

Respond with ONLY valid JSON, no other text.
"""
            
            # Send to Gemini
            try:
                response = self.model.generate_content([prompt, image])
                
                if not response or not response.text:
                    logger.error("Empty response from Gemini")
                    return self._fallback_analysis()
                
                logger.info(f"📥 Gemini raw response: {response.text[:300]}...")
                
                # Parse JSON response
                result = self._parse_gemini_response(response.text)
                
                logger.info(f"🔬 Analysis: {result['disease']} ({result['confidence']*100:.1f}%)")
                
                return result
                
            except Exception as api_error:
                logger.error(f"Gemini API call failed: {api_error}")
                return self._fallback_analysis()
            
        except Exception as e:
            logger.error(f"❌ Gemini analysis error: {e}")
            return self._fallback_analysis()
    
    def _parse_gemini_response(self, response_text):
        """
        Parse Gemini's JSON response
        """
        try:
            # Extract JSON from response (handle markdown formatting)
            json_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if '```' in json_text:
                # Find content between ```json and ```
                parts = json_text.split('```')
                for part in parts:
                    if part.strip().startswith('json'):
                        json_text = part.strip()[4:].strip()
                        break
                    elif part.strip().startswith('{'):
                        json_text = part.strip()
                        break
            
            json_text = json_text.strip()
            
            # Parse JSON
            data = json.loads(json_text)
            
            # Validate and format
            return {
                "success": data.get('is_plant', True),
                "disease": data.get('disease', 'Unknown'),
                "confidence": float(data.get('confidence', 0.75)),
                "severity": data.get('severity', 'Unknown'),
                "description": data.get('description', 'Analysis completed'),
                "treatment": data.get('treatment', 'Consult agricultural expert'),
                "prevention": data.get('prevention', 'Monitor regularly')
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Response text was: {json_text[:200]}")
            return self._fallback_analysis()
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return self._fallback_analysis()
    
    def _fallback_analysis(self):
        """
        Fallback if Gemini unavailable
        """
        logger.warning("⚠️ Using fallback analysis")
        return {
            "success": False,
            "disease": "Service Unavailable",
            "confidence": 0.0,
            "severity": "Error",
            "description": "AI service temporarily unavailable. Please check your internet connection.",
            "treatment": "Verify network connectivity",
            "prevention": "Ensure stable internet connection"
        }

detector = PlantDiseaseDetector()
