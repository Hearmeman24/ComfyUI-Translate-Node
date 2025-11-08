import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TranslateNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "translate"
    CATEGORY = "text"
    
    def translate(self, text):
        logger.info(f"TranslateNode: Received input text (length: {len(text) if text else 0})")
        
        if not text or not text.strip():
            logger.warning("TranslateNode: Empty input text, returning empty string")
            return ("",)
        
        try:
            logger.info(f"TranslateNode: Translating text: '{text[:50]}...' (truncated)")
            translator = GoogleTranslator(source='en', target='zh-CN')
            translated = translator.translate(text)
            logger.info(f"TranslateNode: Translation successful. Result: '{translated[:50]}...' (truncated)")
            logger.info(f"TranslateNode: Returning translated text (length: {len(translated)})")
            return (translated,)
        except Exception as e:
            logger.error(f"TranslateNode: Translation error: {e}", exc_info=True)
            print(f"Translation error: {e}")
            return (text,)

NODE_CLASS_MAPPINGS = {
    "TranslateNode": TranslateNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TranslateNode": "Translate EN to ZH-CN"
}

