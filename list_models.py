import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDkrgEPkgxdY_lz9tLJ8c6eAKCnsFyUCJ0"

genai.configure(api_key=GEMINI_API_KEY)

print("\n" + "="*60)
print("🔍 AVAILABLE GEMINI MODELS FOR YOUR API KEY:")
print("="*60)

try:
    models = genai.list_models()
    
    vision_models = []
    
    for model in models:
        print(f"\n📋 Model: {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Supported Methods: {model.supported_generation_methods}")
        
        # Check if it supports generateContent and vision
        if 'generateContent' in model.supported_generation_methods:
            vision_models.append(model.name)
            print(f"   ✅ Can be used for image analysis!")
    
    print("\n" + "="*60)
    print("✨ MODELS YOU CAN USE:")
    print("="*60)
    for model_name in vision_models:
        print(f"✅ {model_name}")
    
    print("\n")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("\n💡 Your API key might not be activated or valid.")
    print("   Go to: https://makersuite.google.com/app/apikey")
    print("   And verify your API key is enabled.\n")

