from __future__ import annotations

from google import genai
from google.genai import types


def extract_image_bytes(content: bytes, gemini_client: genai.Client, mime_type: str | None = None) -> str:
    """Extract text and interpretation from an image using Gemini 1.5 Flash."""
    try:
        # Using Gemini 3 Flash as it is available in the list of models
        model_id = "gemini-3-flash-preview"
        
        # Default to image/jpeg if mime_type is not provided or not starting with image/
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/jpeg"
        
        prompt = (
            "Analyse cette image de manière détaillée. "
            "Si elle contient du texte, transcris-le intégralement. "
            "Décris également ce que tu vois (objets, contexte, personnes, ambiance) "
            "pour que le contenu soit parfaitement indexé et retrouvable par une recherche textuelle."
        )
        
        response = gemini_client.models.generate_content(
            model=model_id,
            contents=[
                prompt,
                types.Part.from_bytes(data=content, mime_type=mime_type)
            ]
        )
        
        return response.text if response.text else ""
    except Exception as e:
        print(f"Error extracting image with Gemini: {str(e)}")
        return ""
