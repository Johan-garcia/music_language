// src/services/authService.js
import axios from "axios";

// URL base del backend
const API_URL = "http://127.0.0.1:8000/api/v1/auth"; // ajusta según tu configuración real

// --- REGISTRO DE USUARIO ---
export const registerUser = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
  } catch (error) {
    console.error("Error al registrar usuario:", error);
    throw error.response?.data || error.message;
  }
};

// --- LOGIN / TOKEN ---
export const loginUser = async (email, password) => {
  try {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);

    const response = await axios.post(`${API_URL}/token`, params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    // Guardamos el token en localStorage
    localStorage.setItem("access_token", response.data.access_token);
    return response.data;
  } catch (error) {
    console.error("Error en el inicio de sesión:", error);
    throw error.response?.data || error.message;
  }
};

// --- OBTENER USUARIO AUTENTICADO ---
export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No hay token disponible");

    const response = await axios.get(`${API_URL}/me`, {
      headers: { Authorization: `Bearer ${token}` },
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
