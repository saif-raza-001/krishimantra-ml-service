import google.generativeai as genai
import logging
import os

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDkrgEPkgxdY_lz9tLJ8c6eAKCnsFyUCJ0')

class FarmingChatbot:
    def __init__(self):
        logger.info("💬 Initializing AI Farming Chatbot...")
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Chatbot ready!")
            
        except Exception as e:
            logger.error(f"❌ Chatbot initialization failed: {e}")
            self.model = None
    
    def get_response(self, user_message, user_name="Farmer"):
        """
        Get AI response to user's farming question
        """
        try:
            if not self.model:
                return {
                    "reply": "I'm having trouble connecting right now. Please try again!",
                    "success": False
                }
            
            # Personalized system context with user's name
            system_context = f"""
You are an expert agricultural AI assistant helping {user_name}, a farmer, with farming questions.

Your expertise includes:
- Crop diseases and pest management
- Soil health and fertilization
- Irrigation and water management
- Crop selection and rotation
- Weather impact on farming
- Organic farming practices
- Market trends and pricing
- Sustainable agriculture

Guidelines:
1. Address the farmer by name ({user_name}) occasionally to be personal and friendly
2. Be encouraging and supportive - farming is hard work!
3. Provide practical, actionable advice they can implement
4. Use simple language (avoid overly technical jargon)
5. If asked about non-farming topics, politely redirect to farming
6. Always prioritize sustainable and safe farming practices
7. Keep responses concise (2-3 paragraphs max, unless detailed explanation needed)
8. Use emojis occasionally to be friendly 🌾
9. If you give specific product recommendations, mention they're general suggestions

Remember: You're helping {user_name} succeed in their farming journey!
"""
            
            # Combine context with user message
            full_prompt = f"{system_context}\n\n{user_name}'s Question: {user_message}\n\nYour Response:"
            
            # Get response from Gemini
            response = self.model.generate_content(full_prompt)
            
            if not response or not response.text:
                return {
                    "reply": f"I'm sorry {user_name}, I couldn't generate a response. Could you rephrase your question?",
                    "success": False
                }
            
            reply = response.text.strip()
            
            logger.info(f"✅ Generated response for {user_name} ({len(reply)} chars)")
            
            return {
                "reply": reply,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return {
                "reply": f"I apologize {user_name}, but I'm having trouble right now. As your farming assistant, I'm here to help with crops, soil, diseases, and farming techniques. Please try asking again!",
                "success": False
            }

chatbot = FarmingChatbot()
