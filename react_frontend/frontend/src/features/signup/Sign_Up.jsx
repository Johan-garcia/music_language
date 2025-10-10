import { useState } from "react";
import { registerUser } from "../../services/authService";
import "./Sign_Up.css";

const SignUp = ({ onSignUpSuccess, goToLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    full_name: "",
    preferred_language: "es"
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    
    // Validaciones
    if (formData.password !== formData.confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    if (formData.password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    if (!formData.full_name.trim()) {
      setError("El nombre completo es requerido");
      return;
    }

    // Validar email básico
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError("Por favor ingresa un email válido");
      return;
    }

    setLoading(true);

    try {
      // Datos que se envían al backend
      const userData = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        preferred_language: formData.preferred_language
      };

      console.log("📤 Enviando datos de registro:", userData);
      
      const response = await registerUser(userData);
      
      console.log("✅ Registro exitoso:", response);
      
      setMessage("✅ Usuario registrado correctamente. Redirigiendo al login...");
      
      // Limpiar formulario
      setFormData({
        email: "",
        password: "",
        confirmPassword: "",
        full_name: "",
        preferred_language: "es"
      });

      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        goToLogin();
      }, 2000);

    } catch (err) {
      console.error("❌ Error al registrar:", err);
      
      // Manejo mejorado de errores
      if (err.detail) {
        if (err.detail === "Email already registered") {
          setError("Este email ya está registrado. Intenta con otro o inicia sesión.");
        } else {
          setError(err.detail);
        }
      } else if (err.message) {
        setError(err.message);
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError("Error al registrarte. Por favor verifica tu conexión e intenta nuevamente.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup">
      <h2>🎵 Crear cuenta</h2>
      <p>Únete y descubre música nueva</p>
      
      <form onSubmit={handleSignUp} className="signup-form">
        <input
          type="text"
          name="full_name"
          placeholder="Nombre completo"
          value={formData.full_name}
          onChange={handleChange}
          required
          disabled={loading}
        />
        
        <input
          type="email"
          name="email"
          placeholder="Correo electrónico"
          value={formData.email}
          onChange={handleChange}
          required
          disabled={loading}
        />
        
        <input
          type="password"
          name="password"
          placeholder="Contraseña (mínimo 6 caracteres)"
          value={formData.password}
          onChange={handleChange}
          required
          disabled={loading}
          minLength={6}
        />
        
        <input
          type="password"
          name="confirmPassword"
          placeholder="Confirmar contraseña"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          disabled={loading}
        />

        <div className="language-selector">
          <label htmlFor="language">Idioma preferido:</label>
          <select
            id="language"
            name="preferred_language"
            value={formData.preferred_language}
            onChange={handleChange}
            disabled={loading}
          >
            <option value="es"> Español</option>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="pt">Português</option>
            <option value="de">Deutsch</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Registrando..." : "Crear cuenta"}
        </button>
      </form>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <p>
        ¿Ya tienes cuenta?{" "}
        <span className="link" onClick={goToLogin}>
          Inicia sesión
        </span>
      </p>
    </div>
  );
};

export default SignUp;