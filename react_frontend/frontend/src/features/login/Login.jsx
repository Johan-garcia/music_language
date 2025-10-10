import { useState } from "react";
import { loginUser } from "../../services/authService";
import "./Login.css";

const Login = ({ onLoginSuccess, onSwitchToSignUp }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await loginUser(email, password);
      localStorage.setItem("access_token", response.access_token);
      onLoginSuccess(); // 👈 Llama al cambio de vista
    } catch {
      setError("Correo o contraseña incorrectos");
    }
  };

  return (
    <div className="login">
      <h2>Iniciar Sesión</h2>
      <form onSubmit={handleLogin} className="login-form">
        <input
          type="text"
          placeholder="Correo"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Entrar</button>
      </form>

      {error && <p className="error">{error}</p>}

      <p>
        ¿No tienes cuenta?{" "}
        <span className="link" onClick={onSwitchToSignUp}>
          Regístrate aquí
        </span>
      </p>
    </div>
  );
};

export default Login;
