// src/services/authService.js
import axios from "axios";

// URL base del backend
const API_URL = "http://127.0.0.1:8000/api/v1/auth";

// Configuración global de axios
axios.defaults.withCredentials = false;

// --- REGISTRO DE USUARIO ---
export const registerUser = async (userData) => {
  try {
    console.log(" Enviando petición de registro a:", `${API_URL}/register`);
    console.log(" Datos:", userData);
    
    const response = await axios.post(`${API_URL}/register`, userData, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    console.log(" Respuesta del servidor:", response.data);
    return response.data;
  } catch (error) {
    console.error(" Error al registrar usuario:", error);
    console.error(" Detalles del error:", error.response?.data);
    
    
    if (error.response?.data) {
      throw error.response.data;
    } else if (error.message) {
      throw { detail: error.message };
    } else {
      throw { detail: "Error de conexión con el servidor" };
    }
  }
};

// --- LOGIN / TOKEN ---
export const loginUser = async (email, password) => {
  try {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);

    const response = await axios.post(`${API_URL}/token`, params, {
      headers: { 
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    // Guardamos el token en localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }
    
    return response.data;
  } catch (error) {
    console.error("Error en el inicio de sesión:", error);
    console.error("Detalles:", error.response?.data);
    
    if (error.response?.data) {
      throw error.response.data;
    } else {
      throw { detail: "Error de conexión con el servidor" };
    }
  }
};

// --- OBTENER USUARIO AUTENTICADO ---
export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No hay token disponible");

    const response = await axios.get(`${API_URL}/me`, {
      headers: { 
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener el usuario:", error);
    throw error.response?.data || error.message;
  }
};

// --- LOGOUT ---
export const logoutUser = () => {
  localStorage.removeItem("access_token");
};