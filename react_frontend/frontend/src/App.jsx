import { useState } from "react";
import Login from "./features/login/Login";
import SignUp from "./features/signup/Sign_Up";
import Home from "./features/home/Home";
import "./App.css";

function App() {
  // Página actual ("login", "signup" o "home")
  const [currentPage, setCurrentPage] = useState("login");

  // Simulación de inicio de sesión exitoso
  const handleLoginSuccess = () => {
    setCurrentPage("home");
  };

  // Simulación de registro exitoso
  const handleSignUpSuccess = () => {
    setCurrentPage("login"); // vuelve al login después del registro
  };

  // Renderiza la vista según la ruta
  return (
    <div className="app-container">
      {currentPage === "login" && (
        <Login
          onLoginSuccess={handleLoginSuccess}
          goToSignUp={() => setCurrentPage("signup")}
        />
      )}

      {currentPage === "signup" && (
        <SignUp
          onSignUpSuccess={handleSignUpSuccess}
          goToLogin={() => setCurrentPage("login")}
        />
      )}

      {currentPage === "home" && <Home />}
    </div>
  );
}

export default App;
