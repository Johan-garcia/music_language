import { useState } from "react";
import { searchMusic } from "../services/musicService";
import "./MusicSearch.css";

const MusicSearch = ({ onSongSelect }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [language, setLanguage] = useState("es");

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError(" Ingresa el nombre de una canción o artista");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await searchMusic(query, language, 10);
      
      if (response.songs && response.songs.length > 0) {
        setResults(response.songs);
        console.log(` Se encontraron ${response.total} canciones`);
      } else {
        setError("No se encontraron resultados");
      }
    } catch (err) {
      console.error("Error en búsqueda:", err);
      setError(err.detail || "Error al buscar música. Intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleSongClick = (song) => {
    console.log("🎵 Canción seleccionada:", song);
    if (onSongSelect) {
      onSongSelect(song);
    }
  };

  return (
    <div className="music-search">
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            placeholder="Buscar canciones, artistas, álbumes..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            className="search-input"
          />
          
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="language-select"
            disabled={loading}
          >
            <option value="es">🇪🇸 Español</option>
            <option value="en">🇺🇸 English</option>
            <option value="fr">🇫🇷 Français</option>
            <option value="pt">🇧🇷 Português</option>
            <option value="de">🇩🇪 Deutsch</option>
          </select>

          <button type="submit" disabled={loading} className="search-button">
            {loading ? "🔄 Buscando..." : "🔍 Buscar"}
          </button>
        </div>
      </form>

      {error && <div className="error-message">{error}</div>}

      {results.length > 0 && (
        <div className="search-results">
          <h3>Resultados ({results.length})</h3>
          <div className="results-grid">
            {results.map((song) => (
              <div
                key={song.id}
                className="song-card"
                onClick={() => handleSongClick(song)}
              >
                <div className="song-thumbnail">
                  {song.thumbnail_url ? (
                    <img src={song.thumbnail_url} alt={song.title} />
                  ) : (
                    <div className="no-thumbnail">🎵</div>
                  )}
                </div>
                <div className="song-details">
                  <h4 className="song-title">{song.title}</h4>
                  <p className="song-artist">{song.artist}</p>
                  {song.duration && (
                    <span className="song-duration">
                      {Math.floor(song.duration / 60000)}:
                      {Math.floor((song.duration % 60000) / 1000).toString().padStart(2, "0")}
                    </span>
                  )}
                </div>
                <div className="song-play-icon">▶️</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <div className="search-loading">
          <div className="spinner"></div>
          <p>Buscando música...</p>
        </div>
      )}
    </div>
  );
};

export default MusicSearch;