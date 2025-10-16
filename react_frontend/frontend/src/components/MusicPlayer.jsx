import { useState, useEffect } from "react";
import { getStreamingUrl, getLyrics } from "../services/musicService";
import { translateText } from "../services/translationService";
import "./MusicPlayer.css";

const MusicPlayer = ({ song, onClose }) => {
  const [streamingUrl, setStreamingUrl] = useState(null);
  const [lyrics, setLyrics] = useState("");
  const [translatedLyrics, setTranslatedLyrics] = useState("");
  const [showLyrics, setShowLyrics] = useState(true);
  const [loadingLyrics, setLoadingLyrics] = useState(false);
  const [loadingTranslation, setLoadingTranslation] = useState(false);
  const [loadingVideo, setLoadingVideo] = useState(true);
  const [error, setError] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("es");

  useEffect(() => {
    if (song) {
      console.log("🎵 Canción seleccionada:", song.title, "-", song.artist);
      loadStreamingUrl();
      loadLyrics();
    }
  }, [song]);

  const loadStreamingUrl = async () => {
    setLoadingVideo(true);
    setError("");
    
    try {
      if (song.youtube_id && isValidYouTubeId(song.youtube_id)) {
        console.log("✅ YouTube ID encontrado:", song.youtube_id);
        setStreamingUrl(song.youtube_id);
        setLoadingVideo(false);
        return;
      }

      const response = await getStreamingUrl(song.id);
      
      if (response.youtube_url) {
        const videoId = extractYouTubeId(response.youtube_url);
        if (videoId) {
          console.log("✅ ID obtenido del backend:", videoId);
          setStreamingUrl(videoId);
          setLoadingVideo(false);
          return;
        }
      }

      throw new Error("No se encontró video para esta canción");
      
    } catch (err) {
      console.error("❌ Error al cargar video:", err);
      setError(`No se pudo cargar el video: ${err.message}`);
    } finally {
      setLoadingVideo(false);
    }
  };

  const isValidYouTubeId = (id) => {
    if (!id || typeof id !== 'string') return false;
    const youtubeIdRegex = /^[a-zA-Z0-9_-]{11}$/;
    return youtubeIdRegex.test(id);
  };

  const extractYouTubeId = (url) => {
    if (!url) return null;
    if (isValidYouTubeId(url)) return url;
    
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
      /youtube\.com\/embed\/([^&\n?#]+)/,
      /youtube\.com\/v\/([^&\n?#]+)/,
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1] && isValidYouTubeId(match[1])) {
        return match[1];
      }
    }
    
    return null;
  };

  const cleanLyricsText = (text) => {
    let cleaned = text.replace(/🎵.*?\n\n/g, '');
    cleaned = cleaned.replace(/\[Source:.*?\]/g, '');
    cleaned = cleaned.replace(/\(Thanks to.*?\)/g, '');
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
    return cleaned.trim();
  };

  const loadLyrics = async () => {
    setLoadingLyrics(true);
    setError("");
    
    try {
      const response = await getLyrics(song.id);
      
      if (response.lyrics) {
        const cleaned = cleanLyricsText(response.lyrics);
        setLyrics(cleaned);
        setShowLyrics(true);
        console.log("✅ Letras cargadas");
      } else {
        setError("Letras no disponibles");
      }
    } catch (err) {
      console.error("❌ Error al cargar letras:", err);
      setError("Letras no disponibles");
    } finally {
      setLoadingLyrics(false);
    }
  };

  const loadTranslation = async (lang) => {
    setTargetLanguage(lang);
    setLoadingTranslation(true);
    setError("");

    try {
      console.log(`🌍 Traduciendo a: ${lang}`);
      const translated = await translateText(lyrics, lang);
      setTranslatedLyrics(translated);
      console.log("✅ Traducción completada");
    } catch (err) {
      console.error("❌ Error al traducir:", err);
      setTranslatedLyrics("❌ No se pudo traducir las letras.");
    } finally {
      setLoadingTranslation(false);
    }
  };

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    if (newLang && lyrics) {
      loadTranslation(newLang);
    }
  };

  if (!song) return null;

  const embedUrl = streamingUrl 
    ? `https://www.youtube.com/embed/${streamingUrl}?autoplay=1&rel=0` 
    : null;

  return (
    <div className="music-player-overlay fullscreen">
      <div className="music-player-fullscreen">
        
        {/* Header con controles */}
        <header className="player-fullscreen-header">
          <div className="song-info-header">
            <div className="song-thumbnail-mini">
              {song.thumbnail_url ? (
                <img src={song.thumbnail_url} alt={song.title} />
              ) : (
                <div className="no-thumbnail-mini">🎵</div>
              )}
            </div>
            <div className="song-text-info">
              <h2>{song.title}</h2>
              <p>{song.artist}</p>
            </div>
          </div>

          <div className="header-controls">
            <select 
              className="language-selector"
              value={targetLanguage}
              onChange={handleLanguageChange}
              disabled={!lyrics || loadingTranslation}
            >
              <option value="">Selecciona idioma para traducir</option>
              <option value="es">🇪🇸 Español</option>
              <option value="en">🇺🇸 English</option>
              <option value="pt">🇧🇷 Português</option>
              <option value="fr">🇫🇷 Français</option>
              <option value="de">🇩🇪 Deutsch</option>
              <option value="it">🇮🇹 Italiano</option>
              <option value="ja">🇯🇵 日本語</option>
              <option value="ko">🇰🇷 한국어</option>
            </select>

            <button className="close-fullscreen-btn" onClick={onClose}>
              ✕ Cerrar
            </button>
          </div>
        </header>

        {/* Video centrado */}
        <div className="video-section-centered">
          {loadingVideo ? (
            <div className="video-loading-centered">
              <div className="spinner"></div>
              <p>Cargando video...</p>
            </div>
          ) : embedUrl ? (
            <div className="video-container-centered">
              <iframe
                src={embedUrl}
                title={song.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          ) : (
            <div className="no-video-centered">
              <p>⚠️ Video no disponible</p>
            </div>
          )}
        </div>

        {/* Contenido principal: Letras lado a lado */}
        <div className="player-fullscreen-content">
          
          {/* Columna Izquierda: Letra Original */}
          <div className="lyrics-column left-column">
            <div className="lyrics-section-fullscreen">
              <h3>📝 Letra Original</h3>
              {loadingLyrics ? (
                <div className="lyrics-loading">
                  <div className="spinner-small"></div>
                  <p>Cargando letras...</p>
                </div>
              ) : lyrics ? (
                <div className="lyrics-text-fullscreen">
                  {lyrics.split('\n').map((line, index) => (
                    <p key={`original-${index}`} className="lyric-line">
                      {line.trim() || '\u00A0'}
                    </p>
                  ))}
                </div>
              ) : (
                <p className="no-lyrics">Letras no disponibles</p>
              )}
            </div>
          </div>

          {/* Columna Derecha: Letra Traducida */}
          <div className="lyrics-column right-column">
            <div className="lyrics-section-fullscreen">
              <h3>
                🌍 Letra Traducida 
                {targetLanguage && ` (${getLanguageName(targetLanguage)})`}
              </h3>
              
              {!targetLanguage || targetLanguage === "" ? (
                <div className="select-language-prompt">
                  <div className="prompt-icon">🌐</div>
                  <p>Selecciona un idioma arriba para ver la traducción</p>
                </div>
              ) : loadingTranslation ? (
                <div className="lyrics-loading">
                  <div className="spinner-small"></div>
                  <p>Traduciendo a {getLanguageName(targetLanguage)}...</p>
                </div>
              ) : translatedLyrics ? (
                <div className="lyrics-text-fullscreen">
                  {translatedLyrics.split('\n').map((line, index) => (
                    <p key={`translated-${index}`} className="lyric-line">
                      {line.trim() || '\u00A0'}
                    </p>
                  ))}
                </div>
              ) : (
                <p className="no-lyrics">Traducción no disponible</p>
              )}
            </div>
          </div>
        </div>

        {/* Footer con errores si los hay */}
        {error && (
          <div className="player-error-footer">{error}</div>
        )}
      </div>
    </div>
  );
};

// Función auxiliar para nombres de idiomas
const getLanguageName = (code) => {
  const languages = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文'
  };
  return languages[code] || code.toUpperCase();
};

export default MusicPlayer;