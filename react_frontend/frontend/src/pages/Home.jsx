import { useState } from "react";
import MusicSearch from "../components/MusicSearch";
import MusicPlayer from "../components/MusicPlayer";
import "./Home.css";

const Home = ({ user, onLogout }) => {
  const [selectedSong, setSelectedSong] = useState(null);

  const handleSongSelect = (song) => {
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
          <span>👤 {user?.full_name || user?.email}</span>
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

        <MusicSearch onSongSelect={handleSongSelect} />
      </div>

      {selectedSong && (
        <MusicPlayer song={selectedSong} onClose={handleClosePlayer} />
      )}
    </div>
  );
};

export default Home;