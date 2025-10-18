import { useState } from "react";
import { loginUser } from "../../services/authService";
import "./Login.css";

const Login = ({ onLoginSuccess, goToSignUp }) => {  // Verificar este nombre
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const response = await loginUser(email, password);
      console.log("Login exitoso:", response);
      localStorage.setItem("access_token", response.access_token);
      onLoginSuccess();
    } catch (err) {
      console.error("Error de login:", err);
      
      if (err.detail) {
        setError(err.detail);
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError("Error de conexión. Verifica que el backend esté corriendo en el puerto 8000.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login">
      <h2>🎵 Music App</h2>
      <p>Inicia sesión para descubrir música</p>
      
      <form onSubmit={handleLogin} className="login-form">
        <input
          type="text"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={loading}
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Cargando..." : "Iniciar Sesión"}
        </button>
      </form>

      {error && <p className="error"> {error}</p>}

      <p>
        ¿No tienes cuenta?{" "}
        <span className="link" onClick={goToSignUp}>  {/* Verificar esto */}
          Regístrate aquí
        </span>
      </p>

      
    </div>
  );
};

export default Login;