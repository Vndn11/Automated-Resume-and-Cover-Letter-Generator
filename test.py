import google.generativeai as genai

genai.configure(api_key="AIzaSyCK3NPedsUv0AeeSOWjnkIUlT01OIycSkI")

# List available models (this should show if gemini-pro is supported in v1beta)
models = genai.list_models()
for model in models:
    print(model.name, model.supported_generation_methods)