import axios from "axios";

// Usar solo MyMemory API (más estable)
const TRANSLATION_API = "https://api.mymemory.translated.net/get";

export const translateText = async (text, targetLang = "es") => {
  try {
    console.log("🌍 Iniciando traducción...");
    
    const sourceLang = detectLanguageFromText(text);
    console.log(`📝 Idioma detectado: ${sourceLang} → Traduciendo a: ${targetLang}`);

    if (sourceLang === targetLang) {
      console.log("⚠️ El texto ya está en el idioma objetivo");
      return text;
    }

    // Dividir en fragmentos más pequeños
    const maxLength = 400;
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
      console.log(` Traduciendo fragmento ${i + 1}/${chunks.length}...`);
      try {
        const translated = await translateChunk(chunks[i], sourceLang, targetLang);
        translatedChunks.push(translated);
        // Pausa entre peticiones
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (err) {
        console.error(` Error en fragmento ${i + 1}:`, err);
        translatedChunks.push(chunks[i]); // Mantener original si falla
      }
    }

    const result = translatedChunks.join('\n\n');
    console.log("Traducción completada");
    return result;

  } catch (error) {
    console.error(" Error al traducir:", error);
    throw new Error("Error en la traducción");
  }
};


const translateChunk = async (text, sourceLang, targetLang) => {
  try {
    const langPair = `${sourceLang}|${targetLang}`;
    
    const response = await axios.get(TRANSLATION_API, {
      params: {
        q: text,
        langpair: langPair,
      },
      timeout: 10000,
    });

    if (response.data && response.data.responseData) {
      const translated = response.data.responseData.translatedText;
      if (translated && translated !== text) {
        return translated;
      }
    }

    return await translateWithLibreTranslate(text, sourceLang, targetLang);

  } catch (error) {
    // Si es error 429 (rate limit), esperar más tiempo
    if (error.response?.status === 429) {
      console.warn("⏳ Rate limit alcanzado, esperando 2 segundos...");
      await new Promise(resolve => setTimeout(resolve, 2000));
      // Intentar de nuevo con LibreTranslate
      return await translateWithLibreTranslate(text, sourceLang, targetLang);
    }
    
    console.error("Error en traducción de fragmento:", error);
    return text; // Devolver original si falla
  }
};

// Y aumenta el delay en el loop principal:
await new Promise(resolve => setTimeout(resolve, 800)); // De 300ms a 800ms

const detectLanguageFromText = (text) => {
  const lowerText = text.toLowerCase();
  
  const spanishKeywords = ['que', 'para', 'con', 'por', 'una', 'de', 'la', 'el', 'los', 'amor', 'corazón', 'cuando', 'donde'];
  const englishKeywords = ['the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'love', 'heart', 'when', 'where'];
  const portugueseKeywords = ['que', 'para', 'com', 'uma', 'você', 'seu', 'ela', 'mais', 'quando', 'onde', 'amor'];
  const frenchKeywords = ['que', 'pour', 'avec', 'une', 'dans', 'est', 'pas', 'vous', 'amour', 'quand', 'où'];
  const dutchKeywords = ['kom', 'bij', 'ik', 'van', 'wat', 'het', 'een', 'is', 'dat', 'op', 'voor', 'je'];

  let spanishCount = 0;
  let englishCount = 0;
  let portugueseCount = 0;
  let frenchCount = 0;
  let dutchCount = 0;

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

  dutchKeywords.forEach(word => {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    dutchCount += (lowerText.match(regex) || []).length;
  });

  const scores = [
    { lang: 'en', score: englishCount },
    { lang: 'es', score: spanishCount },
    { lang: 'pt', score: portugueseCount },
    { lang: 'fr', score: frenchCount },
    { lang: 'nl', score: dutchCount }
  ];

  scores.sort((a, b) => b.score - a.score);

  console.log("📊 Puntuaciones de detección:", scores);

  if (scores[0].score > 0) {
    return scores[0].lang;
  }

  return 'en';
};

export const getLanguageName = (code) => {
  const languages = {
    'en': 'Inglés',
    'es': 'Español',
    'pt': 'Portugués',
    'fr': 'Francés',
    'de': 'Alemán',
    'it': 'Italiano',
    'nl': 'Holandés'
  };
  return languages[code] || code.toUpperCase();
};