import { useState, useEffect } from "react";
import { getRecommendations } from "../services/musicService";
import axios from "axios";
import "./Recommendations.css";

const Recommendations = ({ onSongSelect, userLanguage = "es" }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [initializing, setInitializing] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, [userLanguage]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError("");
    
    try {
      const response = await getRecommendations(null, userLanguage, 20);
      
      if (response && response.recommendations && response.recommendations.length > 0) {
        setRecommendations(response.recommendations);
        console.log(`✅ ${response.total} recomendaciones cargadas`);
      } else {
        setError("No hay canciones. Haz clic en 'Cargar Canciones' para comenzar.");
        setRecommendations([]);
      }
    } catch (err) {
      console.error("❌ Error:", err);
      setError("No hay canciones disponibles.");
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCleanAndInitialize = async () => {
    if (!confirm("Esto eliminará las canciones de prueba y cargará canciones reales. ¿Continuar?")) {
      return;
    }
    
    setInitializing(true);
    setError("");
    
    try {
      console.log("🧹 Limpiando y cargando canciones reales...");
      
      const token = localStorage.getItem("access_token");
      const response = await axios.post(
        `http://127.0.0.1:8000/api/v1/recommendations/clean-and-initialize?language=${userLanguage}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          timeout: 120000, // 2 minutos
        }
      );
      
      console.log("✅ Resultado:", response.data);
      alert(`✅ Listo!\n\n- Eliminadas: ${response.data.deleted} canciones de prueba\n- Agregadas: ${response.data.added} canciones reales\n\nAhora puedes reproducir los videos.`);
      
      // Recargar
      await loadRecommendations();
      
    } catch (err) {
      console.error("❌ Error:", err);
      alert("❌ Error al cargar. Verifica los logs del backend.");
    } finally {
      setInitializing(false);
    }
  };

  const handleSongClick = (recommendation) => {
    const song = recommendation.song;
    
    if (!song || !song.youtube_id) {
      alert("⚠️ Esta canción no tiene video disponible");
      return;
    }
    
    console.log("🎵 Reproduciendo:", song.title);
    
    if (onSongSelect) {
      onSongSelect(song);
    }
  };

  return (
    <div className="recommendations">
      <div className="recommendations-header">
        <h2>🎵 Recomendaciones para ti</h2>
        
        <div className="header-buttons">
          <button 
            onClick={handleCleanAndInitialize} 
            className="initialize-btn"
            disabled={initializing}
          >
            {initializing ? "⏳ Cargando (30-60s)..." : "🧹 Cargar Canciones"}
          </button>
          
          <button 
            onClick={loadRecommendations} 
            className="refresh-btn"
            disabled={loading}
          >
            🔄 Actualizar
          </button>
        </div>
      </div>

      {initializing && (
        <div className="recommendations-loading">
          <div className="spinner"></div>
          <p><strong>Cargando canciones reales desde YouTube...</strong></p>
          <p>Esto puede tomar 30-60 segundos. Por favor espera.</p>
        </div>
      )}

      {loading && !initializing && (
        <div className="recommendations-loading">
          <div className="spinner"></div>
          <p>Cargando recomendaciones...</p>
        </div>
      )}

      {error && !loading && !initializing && (
        <div className="recommendations-error">
          <p>{error}</p>
          <button onClick={handleCleanAndInitialize} className="retry-btn">
            🧹 Cargar Canciones Reales
          </button>
        </div>
      )}

      {!loading && !initializing && !error && recommendations.length === 0 && (
        <div className="recommendations-empty">
          <p>🎵 No hay canciones disponibles.</p>
          <button onClick={handleCleanAndInitialize} className="initialize-btn-large">
            🧹 Cargar Canciones Reales
          </button>
        </div>
      )}

      {!loading && !initializing && recommendations.length > 0 && (
        <div className="recommendations-grid">
          {recommendations.map((rec, index) => (
            <div
              key={rec.song?.id || index}
              className="recommendation-card"
              onClick={() => handleSongClick(rec)}
            >
              <div className="recommendation-thumbnail">
                {rec.song?.thumbnail_url ? (
                  <img 
                    src={rec.song.thumbnail_url} 
                    alt={rec.song.title}
                  />
                ) : (
                  <div className="no-thumbnail">🎵</div>
                )}
                <div className="play-overlay">
                  <span className="play-icon">▶</span>
                </div>
              </div>
              
              <div className="recommendation-info">
                <h4 className="recommendation-title">
                  {rec.song?.title || "Sin título"}
                </h4>
                <p className="recommendation-artist">
                  {rec.song?.artist || "Desconocido"}
                </p>
                <span className="recommendation-reason">
                  {rec.reason}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;