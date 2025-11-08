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
            # Google Translate has a ~5000 character limit, so split long texts into chunks
            MAX_CHUNK_SIZE = 4500  # Safe limit below 5000
            
            if len(text) <= MAX_CHUNK_SIZE:
                # Short text: translate directly
                logger.info(f"TranslateNode: Translating text directly (length: {len(text)})")
                translated = self._translate_chunk(text)
                if translated:
                    logger.info(f"TranslateNode: Translation successful. Result length: {len(translated)}")
                    return (translated,)
                else:
                    logger.warning("TranslateNode: Translation returned empty, returning original")
                    return (text,)
            else:
                # Long text: split into chunks and translate separately
                logger.info(f"TranslateNode: Text too long ({len(text)} chars), splitting into chunks")
                chunks = self._split_text_into_chunks(text, MAX_CHUNK_SIZE)
                logger.info(f"TranslateNode: Split into {len(chunks)} chunks")
                
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    logger.info(f"TranslateNode: Translating chunk {i+1}/{len(chunks)} (length: {len(chunk)})")
                    translated_chunk = self._translate_chunk(chunk)
                    if translated_chunk:
                        translated_chunks.append(translated_chunk)
                    else:
                        logger.warning(f"TranslateNode: Chunk {i+1} translation failed, using original")
                        translated_chunks.append(chunk)
                
                translated = " ".join(translated_chunks)
                logger.info(f"TranslateNode: All chunks translated. Final result length: {len(translated)}")
                return (translated,)
                
        except Exception as e:
            logger.error(f"TranslateNode: Translation error: {e}", exc_info=True)
            print(f"Translation error: {e}")
            return (text,)
    
    def _split_text_into_chunks(self, text, max_size):
        """Split text into chunks, trying to break at sentence boundaries."""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Try to split by sentences first
        sentences = text.replace('. ', '.\n').replace('! ', '!\n').replace('? ', '?\n').split('\n')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed limit, save current chunk and start new one
            if current_chunk and len(current_chunk) + len(sentence) + 1 > max_size:
                chunks.append(current_chunk)
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # If still too long, split by character limit
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_size:
                final_chunks.append(chunk)
            else:
                # Force split by character limit
                for i in range(0, len(chunk), max_size):
                    final_chunks.append(chunk[i:i+max_size])
        
        return final_chunks
    
    def _translate_chunk(self, chunk):
        """Translate a single chunk and handle the concatenation bug."""
        translator = GoogleTranslator(source='en', target='zh-CN')
        translated = translator.translate(chunk)
        
        # Fix: deep-translator sometimes returns original text + translation concatenated
        # Extract only the translated portion if original text is prepended
        if translated and translated.startswith(chunk):
            actual_translated = translated[len(chunk):].strip()
            if actual_translated:
                logger.debug("TranslateNode: Removed prepended original text from chunk translation")
                return actual_translated
            else:
                logger.warning("TranslateNode: No distinct translation found after removing original text")
                return None
        
        return translated

NODE_CLASS_MAPPINGS = {
    "TranslateNode": TranslateNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TranslateNode": "Translate EN to ZH-CN"
}

