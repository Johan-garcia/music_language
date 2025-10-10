import { useState } from "react";
import "./Home.css";

const Home = ({ user, onLogout }) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Buscando:", searchQuery);
    // Aquí implementarás la búsqueda de música
  };

  return (
    <div className="home">
      <header className="home-header">
        <div className="logo">
          <h1>🎵 Music App</h1>
        </div>
        <div className="user-info">
          <span>👤 {user?.full_name || user?.email}</span>
          <button onClick={onLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </div>
      </header>

      <div className="home-content">
        <div className="welcome-banner">
          <h2>Bienvenido, {user?.full_name || "Usuario"}</h2>
          <p>Descubre y disfruta tu música favorita</p>
        </div>

        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              placeholder="Buscar canciones, artistas, álbumes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit">🔍 Buscar</button>
          </form>
        </div>

        <div className="music-categories">
          <h3>Categorías</h3>
          <div className="categories-grid">
            <div className="category-card">
              <span className="category-icon">🎸</span>
              <h4>Rock</h4>
            </div>
            <div className="category-card">
              <span className="category-icon">🎤</span>
              <h4>Pop</h4>
            </div>
            <div className="category-card">
              <span className="category-icon">🎹</span>
              <h4>Clásica</h4>
            </div>
            <div className="category-card">
              <span className="category-icon">🎧</span>
              <h4>Electrónica</h4>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;