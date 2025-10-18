import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/v1/music";

// Obtener token de autenticación
const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

// Función principal de traducción usando el BACKEND
export const translateText = async (text, targetLang = "en") => {
  console.log(" Iniciando traducción vía backend...");

  if (!text || text.trim().length === 0) {
    return text;
  }

  try {
    const response = await axios.post(
      `${API_URL}/translate`,
      {
        text: text,
        target_lang: targetLang,
        source_lang: "auto",
      },
      {
        headers: getAuthHeaders(),
        params: {
          text: text,
          target_lang: targetLang,
          source_lang: "auto",
        },
        timeout: 60000, // 60 segundos
      }
    );

    console.log(" Traducción completada");
    return response.data.translated;
    
  } catch (error) {
    console.error(" Error al traducir:", error);
    
    if (error.response?.status === 401) {
      throw new Error("No autenticado. Por favor, inicia sesión nuevamente.");
    }
    
    throw new Error(error.response?.data?.detail || "Error al traducir el texto");
  }
};

// Detectar idioma 
export const detectLanguage = (text) => {
  
  return "auto";
};