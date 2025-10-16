// src/services/translationService.js
import axios from "axios";

const TRANSLATION_API = "https://api.mymemory.translated.net/get";

/**
 * Detecta el idioma del texto y traduce al idioma objetivo
 */
export const translateText = async (text, targetLang = "es") => {
  try {
    console.log("🌍 Iniciando traducción...");
    
    // Detectar el idioma del texto original
    const sourceLang = detectLanguageFromText(text);
    console.log(`📝 Idioma detectado: ${sourceLang} → Traduciendo a: ${targetLang}`);

    // Si el idioma origen es el mismo que el destino, no traducir
    if (sourceLang === targetLang) {
      console.log("⚠️ El texto ya está en el idioma objetivo");
      return text;
    }

    // Dividir el texto en fragmentos más pequeños (API tiene límite)
    const maxLength = 450; // Reducido para mayor compatibilidad
    const lines = text.split('\n');
    const chunks = [];
    let currentChunk = '';

    for (const line of lines) {
      if ((currentChunk + line + '\n').length > maxLength) {
        if (currentChunk.trim()) chunks.push(currentChunk.trim());
        currentChunk = line + '\n';
      } else {
        currentChunk += line + '\n';
      }
    }
    if (currentChunk.trim()) chunks.push(currentChunk.trim());

    console.log(`📦 Dividido en ${chunks.length} fragmentos`);

    // Traducir cada fragmento
    const translatedChunks = [];
    for (let i = 0; i < chunks.length; i++) {
      console.log(`📝 Traduciendo fragmento ${i + 1}/${chunks.length}...`);
      try {
        const translated = await translateChunk(chunks[i], sourceLang, targetLang);
        translatedChunks.push(translated);
        // Pequeña pausa para evitar rate limiting
        await new Promise(resolve => setTimeout(resolve, 300));
      } catch (err) {
        console.error(`❌ Error en fragmento ${i + 1}:`, err);
        translatedChunks.push(chunks[i]); // Mantener original si falla
      }
    }

    const result = translatedChunks.join('\n\n');
    console.log("✅ Traducción completada");
    return result;

  } catch (error) {
    console.error("❌ Error al traducir:", error);
    throw new Error("Error en la traducción");
  }
};

/**
 * Traduce un fragmento de texto
 */
const translateChunk = async (text, sourceLang, targetLang) => {
  try {
    const langPair = `${sourceLang}|${targetLang}`;
    
    const response = await axios.get(TRANSLATION_API, {
      params: {
        q: text,
        langpair: langPair,
      },
      timeout: 10000, // 10 segundos timeout
    });

    if (response.data && response.data.responseData) {
      const translated = response.data.responseData.translatedText;
      
      // Verificar si la traducción fue exitosa
      if (translated && translated !== text) {
        return translated;
      }
    }

    // Si no hay traducción válida, intentar con API alternativa
    return await translateWithLibreTranslate(text, sourceLang, targetLang);

  } catch (error) {
    console.error("Error en traducción de fragmento:", error);
    // Intentar API alternativa
    try {
      return await translateWithLibreTranslate(text, sourceLang, targetLang);
    } catch (err) {
      return text; // Devolver texto original si todo falla
    }
  }
};

/**
 * API alternativa de traducción (LibreTranslate - instancia pública)
 */
const translateWithLibreTranslate = async (text, sourceLang, targetLang) => {
  try {
    const response = await axios.post(
      "https://libretranslate.de/translate",
      {
        q: text,
        source: sourceLang,
        target: targetLang,
        format: "text"
      },
      {
        headers: {
          "Content-Type": "application/json"
        },
        timeout: 10000
      }
    );

    if (response.data && response.data.translatedText) {
      return response.data.translatedText;
    }

    throw new Error("No se recibió traducción de LibreTranslate");
  } catch (error) {
    console.error("Error con LibreTranslate:", error);
    throw error;
  }
};

/**
 * Detecta el idioma del texto basándose en palabras clave y patrones
 */
const detectLanguageFromText = (text) => {
  const lowerText = text.toLowerCase();
  
  // Palabras clave en español
  const spanishKeywords = [
    'que', 'para', 'con', 'por', 'una', 'de', 'la', 'el', 'los', 'las',
    'yo', 'tu', 'él', 'ella', 'nosotros', 'amor', 'corazón', 'vida',
    'cuando', 'donde', 'porque', 'como', 'desde', 'hasta'
  ];
  
  // Palabras clave en inglés
  const englishKeywords = [
    'the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his',
    'they', 'one', 'have', 'this', 'from', 'love', 'heart', 'baby',
    'when', 'where', 'what', 'how', 'like', 'just', 'know'
  ];
  
  // Palabras clave en portugués
  const portugueseKeywords = [
    'que', 'para', 'com', 'uma', 'você', 'seu', 'ela', 'mais',
    'quando', 'onde', 'porque', 'como', 'desde', 'até', 'amor'
  ];
  
  // Palabras clave en francés
  const frenchKeywords = [
    'que', 'pour', 'avec', 'une', 'dans', 'est', 'pas', 'vous',
    'amour', 'coeur', 'quand', 'où', 'comment', 'comme'
  ];

  // Contar coincidencias
  let spanishCount = 0;
  let englishCount = 0;
  let portugueseCount = 0;
  let frenchCount = 0;

  spanishKeywords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    spanishCount += (lowerText.match(regex) || []).length;
  });

  englishKeywords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    englishCount += (lowerText.match(regex) || []).length;
  });

  portugueseKeywords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    portugueseCount += (lowerText.match(regex) || []).length;
  });

  frenchKeywords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    frenchCount += (lowerText.match(regex) || []).length;
  });

  // Determinar el idioma con más coincidencias
  const scores = [
    { lang: 'en', score: englishCount },
    { lang: 'es', score: spanishCount },
    { lang: 'pt', score: portugueseCount },
    { lang: 'fr', score: frenchCount }
  ];

  scores.sort((a, b) => b.score - a.score);

  console.log("📊 Puntuaciones de detección:", scores);

  // Si el inglés tiene más coincidencias, es inglés
  if (scores[0].score > 0) {
    return scores[0].lang;
  }

  // Por defecto, asumir inglés (mayoría de canciones)
  return 'en';
};

/**
 * Obtiene el nombre completo del idioma
 */
export const getLanguageName = (code) => {
  const languages = {
    'en': 'Inglés',
    'es': 'Español',
    'pt': 'Portugués',
    'fr': 'Francés',
    'de': 'Alemán',
    'it': 'Italiano',
    'ja': 'Japonés',
    'ko': 'Coreano',
    'zh': 'Chino'
  };
  return languages[code] || code.toUpperCase();
};