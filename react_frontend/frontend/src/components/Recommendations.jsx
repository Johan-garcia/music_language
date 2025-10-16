import { useState, useEffect } from "react";
import { getRecommendations, getAvailableGenres } from "../services/musicService";
import "./Recommendations.css";

const Recommendations = ({ onSongSelect, userLanguage = "es" }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadGenres();
    loadRecommendations();
  }, []);

  const loadGenres = async () => {
    try {
      const genresList = await getAvailableGenres();
      setGenres(genresList);
    } catch (err) {
      console.error("Error al cargar géneros:", err);
    }
  };

  const loadRecommendations = async (genre = null) => {
    setLoading(true);
    setError("");
    
    try {
      const response = await getRecommendations(genre, userLanguage, 12);
      
      if (response.recommendations && response.recommendations.length > 0) {
        setRecommendations(response.recommendations);
        console.log(`✅ ${response.total} recomendaciones cargadas`);
      } else {
        setError("No se encontraron recomendaciones");
      }
    } catch (err) {
      console.error("Error al cargar recomendaciones:", err);
      setError("Error al cargar recomendaciones. Intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenreChange = (genre) => {
    setSelectedGenre(genre);
    loadRecommendations(genre || null);
  };

  const handleSongClick = (recommendation) => {
    if (onSongSelect) {
      onSongSelect(recommendation.song);
    }
  };

  return (
    <div className="recommendations">
      <div className="recommendations-header">
        <h2>🎵 Recomendaciones para ti</h2>
        
        <div className="genre-filter">
          <select
            value={selectedGenre}
            onChange={(e) => handleGenreChange(e.target.value)}
            className="genre-select"
            disabled={loading}
          >
            <option value="">Todos los géneros</option>
            {genres.map((genre) => (
              <option key={genre} value={genre}>
                {genre.charAt(0).toUpperCase() + genre.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="recommendations-loading">
          <div className="spinner"></div>
          <p>Cargando recomendaciones...</p>
        </div>
      )}

      {error && <div className="recommendations-error">{error}</div>}

      {!loading && recommendations.length > 0 && (
        <div className="recommendations-grid">
          {recommendations.map((rec, index) => (
            <div
              key={rec.song.id || index}
              className="recommendation-card"
              onClick={() => handleSongClick(rec)}
            >
              <div className="recommendation-thumbnail">
                {rec.song.thumbnail_url ? (
                  <img src={rec.song.thumbnail_url} alt={rec.song.title} />
                ) : (
                  <div className="no-thumbnail">🎵</div>
                )}
                <div className="play-overlay">
                  <span className="play-icon">▶</span>
                </div>
              </div>
              
              <div className="recommendation-info">
                <h4 className="recommendation-title">{rec.song.title}</h4>
                <p className="recommendation-artist">{rec.song.artist}</p>
                <span className="recommendation-reason">{rec.reason}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;