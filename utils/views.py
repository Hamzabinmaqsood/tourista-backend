from django.shortcuts import render

# Create your views here.
# In utils/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from googletrans import Translator, LANGUAGES

class TranslationView(APIView):
    """
    API endpoint for translating text.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Accepts text and a target language, returns the translation.
        """
        text_to_translate = request.data.get('text')
        target_language = request.data.get('target_language') # e.g., 'ur' for Urdu

        if not text_to_translate or not target_language:
            return Response(
                {"error": "Both 'text' and 'target_language' fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the target language code is valid
        if target_language not in LANGUAGES:
             return Response(
                {"error": f"Invalid target_language code. Please use one of: {list(LANGUAGES.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            translator = Translator()
            translation = translator.translate(text_to_translate, dest=target_language)
            
            response_data = {
                "original_text": translation.origin,
                "translated_text": translation.text,
                "source_language": LANGUAGES.get(translation.src, translation.src),
                "target_language": LANGUAGES.get(translation.dest, translation.dest)
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Translation service failed.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )