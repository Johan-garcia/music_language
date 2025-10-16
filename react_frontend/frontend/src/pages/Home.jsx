import { useState } from "react";
import MusicSearch from "../components/MusicSearch";
import MusicPlayer from "../components/MusicPlayer";
import Recommendations from "../components/Recommendations";
import "./Home.css";

const Home = ({ user, onLogout }) => {
  const [selectedSong, setSelectedSong] = useState(null);
  const [activeTab, setActiveTab] = useState("search");

  const handleSongSelect = (song) => {
    console.log("🎵 Canción seleccionada en Home:", song);
    setSelectedSong(song);
  };

  const handleClosePlayer = () => {
    setSelectedSong(null);
  };

  return (
    <div className="home">
      <header className="home-header">
        <div className="logo">
          <h1>🎵 Music Language</h1>
        </div>
        <div className="user-info">
          <span className="user-name">👤 {user?.full_name || user?.email}</span>
          <button onClick={onLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </div>
      </header>

      <div className="home-content">
        <div className="welcome-banner">
          <h2>Bienvenido, {user?.full_name || "Usuario"}</h2>
          <p>Descubre y disfruta tu música favorita con traducción de letras</p>
        </div>

        {/* Tabs de navegación */}
        <div className="content-tabs">
          <button
            className={`tab-button ${activeTab === "search" ? "active" : ""}`}
            onClick={() => setActiveTab("search")}
          >
            🔍 Buscar Música
          </button>
          <button
            className={`tab-button ${activeTab === "recommendations" ? "active" : ""}`}
            onClick={() => setActiveTab("recommendations")}
          >
            ⭐ Recomendaciones
          </button>
        </div>

        {/* Contenido según tab activo */}
        {activeTab === "search" && (
          <MusicSearch onSongSelect={handleSongSelect} />
        )}

        {activeTab === "recommendations" && (
          <Recommendations 
            onSongSelect={handleSongSelect}
            userLanguage={user?.preferred_language || "es"}
          />
        )}
      </div>

      {/* Reproductor modal (mantiene el diseño original) */}
      {selectedSong && (
        <MusicPlayer song={selectedSong} onClose={handleClosePlayer} />
      )}
    </div>
  );
};

export default Home;