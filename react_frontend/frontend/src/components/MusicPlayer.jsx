import { useState, useEffect } from "react";
import { getStreamingUrl, getLyrics } from "../services/musicService";
import "./MusicPlayer.css";

const MusicPlayer = ({ song, onClose }) => {
  const [streamingUrl, setStreamingUrl] = useState(null);
  const [lyrics, setLyrics] = useState("");
  const [showLyrics, setShowLyrics] = useState(false);
  const [loadingLyrics, setLoadingLyrics] = useState(false);
  const [loadingVideo, setLoadingVideo] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (song) {
      console.log("🎵 Canción seleccionada:", song);
      loadStreamingUrl();
    }
  }, [song]);

  const loadStreamingUrl = async () => {
    setLoadingVideo(true);
    setError("");
    
    try {
      // Si la canción ya tiene youtube_id, usarlo directamente
      if (song.youtube_id) {
        console.log("✅ YouTube ID encontrado:", song.youtube_id);
        setStreamingUrl(song.youtube_id);
        setLoadingVideo(false);
        return;
      }

      // Si no, intentar obtenerlo del backend
      const response = await getStreamingUrl(song.id);
      console.log("📡 Respuesta del backend:", response);
      
      if (response.youtube_url) {
        // Extraer el ID de la URL
        const videoId = extractYouTubeId(response.youtube_url);
        if (videoId) {
          setStreamingUrl(videoId);
        } else {
          throw new Error("No se pudo extraer el ID del video");
        }
      } else {
        throw new Error("No hay URL de YouTube disponible");
      }
    } catch (err) {
      console.error("❌ Error al cargar URL:", err);
      setError("No se pudo cargar el reproductor. Esta canción no tiene video disponible.");
    } finally {
      setLoadingVideo(false);
    }
  };

  // Función para extraer el ID de YouTube de diferentes formatos de URL
  const extractYouTubeId = (url) => {
    if (!url) return null;
    
    // Si ya es solo el ID (11 caracteres)
    if (url.length === 11 && !url.includes('/') && !url.includes('=')) {
      return url;
    }
    
    // Diferentes formatos de URL de YouTube
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
      /youtube\.com\/embed\/([^&\n?#]+)/,
      /youtube\.com\/v\/([^&\n?#]+)/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        return match[1];
      }
    }
    
    return null;
  };

  const loadLyrics = async () => {
    if (lyrics) {
      setShowLyrics(!showLyrics);
      return;
    }

    setLoadingLyrics(true);
    setError("");
    
    try {
      const response = await getLyrics(song.id);
      console.log("📝 Letras recibidas:", response);
      
      if (response.lyrics) {
        setLyrics(response.lyrics);
        setShowLyrics(true);
      } else {
        setError("Letras no disponibles para esta canción");
      }
    } catch (err) {
      console.error("❌ Error al cargar letras:", err);
      setError("Letras no disponibles para esta canción");
      setTimeout(() => setError(""), 3000);
    } finally {
      setLoadingLyrics(false);
    }
  };

  if (!song) return null;

  const embedUrl = streamingUrl 
    ? `https://www.youtube.com/embed/${streamingUrl}?autoplay=1&rel=0` 
    : null;

  return (
    <div className="music-player-overlay" onClick={onClose}>
      <div className="music-player-container" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>

        <div className="player-header">
          <h2>{song.title}</h2>
          <p>{song.artist}</p>
        </div>

        <div className="player-content">
          {loadingVideo ? (
            <div className="video-loading">
              <div className="spinner"></div>
              <p>Cargando video...</p>
            </div>
          ) : embedUrl && !error ? (
            <div className="video-container">
              <iframe
                src={embedUrl}
                title={song.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                referrerPolicy="strict-origin-when-cross-origin"
              ></iframe>
            </div>
          ) : (
            <div className="no-video">
              <span className="no-video-icon">⚠️</span>
              <p>{error || "No se pudo cargar el video"}</p>
              <small>Video ID: {song.youtube_id || "No disponible"}</small>
            </div>
          )}

          <div className="player-controls">
            <button
              className="lyrics-button"
              onClick={loadLyrics}
              disabled={loadingLyrics}
            >
              {loadingLyrics
                ? "⏳ Cargando..."
                : showLyrics
                ? "📝 Ocultar Letra"
                : "📝 Ver Letra"}
            </button>
          </div>

          {showLyrics && lyrics && (
            <div className="lyrics-container">
              <h3>Letra de la canción</h3>
              <div className="lyrics-text">
                {lyrics.split('\n').map((line, index) => (
                  <p key={index} className="lyric-line">
                    {line.trim() || '\u00A0'}
                  </p>
                ))}
              </div>
            </div>
          )}

          {error && showLyrics && (
            <div className="player-error">{error}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MusicPlayer;