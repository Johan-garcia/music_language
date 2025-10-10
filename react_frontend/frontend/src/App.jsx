import { useState, useEffect } from "react";
import Login from "./features/login/Login";
import SignUp from "./features/signup/Sign_Up";
import Home from "./pages/Home";
import AdminPanel from "./pages/AdminPanel";
import { getCurrentUser } from "./services/authService";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("login");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verificar si hay un usuario autenticado al cargar la app
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("access_token");
      
      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
          
          // Redirigir según el rol
          if (userData.role === "admin") {
            setCurrentPage("admin");
          } else {
            setCurrentPage("home");
          }
        } catch (error) {
          console.error("Error al verificar autenticación:", error);
          localStorage.removeItem("access_token");
          setCurrentPage("login");
        }
      } else {
        setCurrentPage("login");
      }
      
      setLoading(false);
    };

    checkAuth();
  }, []);

  const handleLoginSuccess = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      
      // Redirigir según el rol del usuario
      if (userData.role === "admin") {
        setCurrentPage("admin");
      } else {
        setCurrentPage("home");
      }
    } catch (error) {
      console.error("Error al obtener usuario:", error);
      setCurrentPage("home"); // Fallback
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setCurrentPage("login");
  };

  const handleSignUpSuccess = () => {
    setCurrentPage("login");
  };

  if (loading) {
    return (
      <div className="app-container loading">
        <div className="spinner"></div>
        <p>Cargando...</p>
      </div>
    );
  }

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

      {currentPage === "home" && (
        <Home 
          user={user} 
          onLogout={handleLogout}
        />
      )}

      {currentPage === "admin" && (
        <AdminPanel 
          user={user} 
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;