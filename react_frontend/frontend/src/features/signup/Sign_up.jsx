import { useState } from "react";
import { registerUser } from "../../services/authService";
import "./Sign_Up.css";

const SignUp = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [language, setLanguage] = useState("es");
  const [message, setMessage] = useState("");

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      await registerUser({ email, password, full_name: fullName, preferred_language: language });
      setMessage("Usuario registrado correctamente. Ahora puedes iniciar sesión.");
    } catch {
      setMessage("Error al registrarte. Intenta nuevamente.");
    }
  };

  return (
    <div className="signup">
      <h2>Crear cuenta</h2>
      <form onSubmit={handleSignUp} className="signup-form">
        <input
          type="text"
          placeholder="Nombre completo"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Correo electrónico"
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
        <button type="submit">Registrarme</button>
      </form>

      {message && <p>{message}</p>}

      <p>
        ¿Ya tienes cuenta?{" "}
        <span className="link" onClick={onSwitchToLogin}>
          Inicia sesión
        </span>
      </p>
    </div>
  );
};

export default SignUp;
