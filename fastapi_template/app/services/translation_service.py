import logging
from typing import Optional
import time
from deep_translator import GoogleTranslator, LibreTranslator, MyMemoryTranslator

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Servicio de traducción usando deep-translator (compatible)
    """
    
    def __init__(self):
        logger.info(" Translation Service initialized")
    
    def translate(self, text: str, target_lang: str = "en", source_lang: str = "auto") -> Optional[str]:
        """
        Traduce texto usando múltiples servicios
        """
        if not text or len(text.strip()) == 0:
            return text
        
        logger.info(f" Traduciendo de {source_lang} a {target_lang}")
        
        
        methods = [
            ("Google Translate", lambda: self._translate_with_google(text, target_lang, source_lang)),
            ("LibreTranslate", lambda: self._translate_with_libre(text, target_lang, source_lang)),
            ("MyMemory", lambda: self._translate_with_mymemory(text, target_lang, source_lang)),
        ]
        
        for method_name, method in methods:
            try:
                logger.info(f"   Intentando {method_name}...")
                result = method()
                
                if result and len(result) > 0:
                    logger.info(f"    Traducido con {method_name}")
                    return result
                    
            except Exception as e:
                logger.error(f"    {method_name} falló: {e}")
                continue
        
        logger.warning("⚠️ No se pudo traducir, devolviendo texto original")
        return text
    
    def _translate_with_google(self, text: str, target_lang: str, source_lang: str) -> Optional[str]:
        """Usa Google Translate vía deep-translator"""
        try:
            
            max_chunk_size = 4500
            
            if len(text) > max_chunk_size:
                chunks = self._split_text(text, max_chunk_size)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"      Traduciendo fragmento {i+1}/{len(chunks)}")
                    
                    translator = GoogleTranslator(source=source_lang, target=target_lang)
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                    
                    time.sleep(0.5)  
                
                return "\n\n".join(translated_chunks)
            else:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                return translator.translate(text)
                
        except Exception as e:
            logger.error(f"Google Translate error: {e}")
            return None
    
    def _translate_with_libre(self, text: str, target_lang: str, source_lang: str) -> Optional[str]:
        """Usa LibreTranslate"""
        try:
            max_chunk_size = 3000
            
            if len(text) > max_chunk_size:
                chunks = self._split_text(text, max_chunk_size)
                translated_chunks = []
                
                for chunk in chunks:
                    translator = LibreTranslator(source=source_lang, target=target_lang)
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                    time.sleep(0.5)
                
                return "\n\n".join(translated_chunks)
            else:
                translator = LibreTranslator(source=source_lang, target=target_lang)
                return translator.translate(text)
                
        except Exception as e:
            logger.error(f"LibreTranslate error: {e}")
            return None
    
    def _translate_with_mymemory(self, text: str, target_lang: str, source_lang: str) -> Optional[str]:
        """Usa MyMemory API"""
        try:
            max_chunk_size = 500
            
            if len(text) > max_chunk_size:
                chunks = self._split_text(text, max_chunk_size)
                translated_chunks = []
                
                for chunk in chunks:
                    translator = MyMemoryTranslator(source=source_lang, target=target_lang)
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                    time.sleep(1)  # Rate limiting estricto
                
                return "\n\n".join(translated_chunks)
            else:
                translator = MyMemoryTranslator(source=source_lang, target=target_lang)
                return translator.translate(text)
                
        except Exception as e:
            logger.error(f"MyMemory error: {e}")
            return None
    
    def _split_text(self, text: str, max_size: int) -> list:
        """Divide texto en fragmentos por líneas"""
        lines = text.split("\n")
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 > max_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks


# Instancia global
translation_service = TranslationService()