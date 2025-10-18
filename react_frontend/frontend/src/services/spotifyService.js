
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/v1/auth";


export const getSpotifyAuthUrl = async () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No hay token disponible");

    const response = await axios.get(`${API_URL}/spotify/auth`, {
      headers: { 
        Authorization: `Bearer ${token}`,
      },
    });
    
    return response.data.auth_url;
  } catch (error) {
    console.error("Error al obtener URL de Spotify:", error);
    throw error.response?.data || error.message;
  }
};


export const handleSpotifyCallback = async (code, state) => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No hay token disponible");

    const response = await axios.post(`${API_URL}/spotify/callback`, {
      code: code,
      state: state
    }, {
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
    });
    
    return response.data;
  } catch (error) {
    console.error("Error en callback de Spotify:", error);
    throw error.response?.data || error.message;
  }
};


export const checkSpotifyConnection = async () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return false;

    
    const response = await axios.get(`${API_URL}/me`, {
      headers: { 
        Authorization: `Bearer ${token}`,
      },
    });
    
    return response.data.spotify_connected || false;
  } catch (error) {
    console.error("Error al verificar conexión Spotify:", error);
    return false;
  }
};