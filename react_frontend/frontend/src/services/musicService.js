// src/services/musicService.js
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/v1/music";
const RECOMMENDATIONS_URL = "http://127.0.0.1:8000/api/v1/recommendations";

// Obtener token de autenticación
const getAuthHeaders = () => {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

// --- BUSCAR MÚSICA ---
export const searchMusic = async (query, language = "es", limit = 10) => {
  try {
    const response = await axios.post(
      `${API_URL}/search`,
      {
        query: query,
        language: language,
        limit: limit,
      },
      {
        headers: getAuthHeaders(),
      }
    );

    console.log("✅ Respuesta de búsqueda:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Error al buscar música:", error);
    throw error.response?.data || { detail: "Error al buscar música" };
  }
};

// --- OBTENER URL DE STREAMING ---
export const getStreamingUrl = async (songId) => {
  try {
    const response = await axios.get(`${API_URL}/stream/${songId}`, {
      headers: getAuthHeaders(),
    });

    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener URL de streaming:", error);
    throw error.response?.data || { detail: "Error al obtener streaming" };
  }
};

// --- OBTENER LETRAS ---
export const getLyrics = async (songId) => {
  try {
    const response = await axios.get(`${API_URL}/lyrics/${songId}`, {
      headers: getAuthHeaders(),
    });

    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener letras:", error);
    throw error.response?.data || { detail: "Letras no disponibles" };
  }
};

// --- OBTENER DETALLES DE CANCIÓN ---
export const getSongDetails = async (songId) => {
  try {
    const response = await axios.get(`${API_URL}/song/${songId}`, {
      headers: getAuthHeaders(),
    });

    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener detalles:", error);
    throw error.response?.data || { detail: "Error al obtener detalles" };
  }
};

// --- OBTENER MÚSICA TRENDING ---
export const getTrendingMusic = async (language = null, limit = 20) => {
  try {
    const params = new URLSearchParams();
    if (language) params.append("language", language);
    params.append("limit", limit);

    const response = await axios.get(`${API_URL}/trending?${params}`, {
      headers: getAuthHeaders(),
    });

    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener trending:", error);
    throw error.response?.data || { detail: "Error al obtener trending" };
  }
};

// --- OBTENER RECOMENDACIONES ---
export const getRecommendations = async (genre = null, language = "es", limit = 20) => {
  try {
    const response = await axios.post(
      `${RECOMMENDATIONS_URL}/`,
      {
        genre: genre,
        language: language,
        limit: limit,
      },
      {
        headers: getAuthHeaders(),
      }
    );

    console.log("✅ Recomendaciones recibidas:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Error al obtener recomendaciones:", error);
    throw error.response?.data || { detail: "Error al obtener recomendaciones" };
  }
};

// --- OBTENER GÉNEROS DISPONIBLES ---
export const getAvailableGenres = async () => {
  try {
    const response = await axios.get(`${RECOMMENDATIONS_URL}/genres`, {
      headers: getAuthHeaders(),
    });

    return response.data.genres;
  } catch (error) {
    console.error("❌ Error al obtener géneros:", error);
    // Géneros por defecto si falla
    return [
      "pop", "rock", "hip-hop", "reggaeton", "salsa", 
      "bachata", "jazz", "classical", "electronic", 
      "indie", "metal", "r-n-b", "country"
    ];
  }
};