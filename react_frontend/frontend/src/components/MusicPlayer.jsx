import { useState, useEffect, useRef } from "react";
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

  // Referencias para los contenedores de letras
  const originalLyricsRef = useRef(null);
  const translatedLyricsRef = useRef(null);
  const isSyncingRef = useRef(false); // Para evitar loops infinitos

  useEffect(() => {
    if (song) {
      console.log("🎵 Canción seleccionada:", song.title, "-", song.artist);
      loadStreamingUrl();
      loadLyrics();
    }
  }, [song]);

  useEffect(() => {
    if (lyrics && !translatedLyrics && targetLanguage) {
      loadTranslation(targetLanguage);
    }
  }, [lyrics]);

  // Función para sincronizar el scroll
  const handleOriginalScroll = (e) => {
    if (isSyncingRef.current) return;
    
    const source = e.target;
    const target = translatedLyricsRef.current;
    
    if (!target) return;
    
    isSyncingRef.current = true;
    
    const scrollPercentage = source.scrollTop / (source.scrollHeight - source.clientHeight);
    const targetScrollTop = scrollPercentage * (target.scrollHeight - target.clientHeight);
    
    target.scrollTop = targetScrollTop;
    
    requestAnimationFrame(() => {
      isSyncingRef.current = false;
    });
  };

  const handleTranslatedScroll = (e) => {
    if (isSyncingRef.current) return;
    
    const source = e.target;
    const target = originalLyricsRef.current;
    
    if (!target) return;
    
    isSyncingRef.current = true;
    
    const scrollPercentage = source.scrollTop / (source.scrollHeight - source.clientHeight);
    const targetScrollTop = scrollPercentage * (target.scrollHeight - target.clientHeight);
    
    target.scrollTop = targetScrollTop;
    
    requestAnimationFrame(() => {
      isSyncingRef.current = false;
    });
  };

  const loadStreamingUrl = async () => {
    setLoadingVideo(true);
    setError("");
    
    try {
      if (song.youtube_id && isValidYouTubeId(song.youtube_id)) {
        setStreamingUrl(song.youtube_id);
        setLoadingVideo(false);
        return;
      }

      const response = await getStreamingUrl(song.id);
      
      if (response.youtube_url) {
        const videoId = extractYouTubeId(response.youtube_url);
        if (videoId) {
          setStreamingUrl(videoId);
          setLoadingVideo(false);
          return;
        }
      }

      throw new Error("No se encontró video para esta canción");
      
    } catch (err) {
      console.error("❌ Error al cargar video:", err);
      setError(`No se pudo cargar el video`);
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
    console.log("🧹 Limpiando letras...");
    
    let cleaned = text;
    cleaned = cleaned.replace(/🎵\s*.*?\n\n/g, '');
    cleaned = cleaned.replace(/\d+\s+Contributors?\n/gi, '');
    cleaned = cleaned.replace(/^.*?\s+Lyrics\n/i, '');
    cleaned = cleaned.replace(/\[Songtekst van.*?\]\n/gi, '');
    cleaned = cleaned.replace(/^\[.*?\]\n/gm, '');
    cleaned = cleaned.replace(/\[Source:.*?\]/gi, '');
    cleaned = cleaned.replace(/\(Thanks to.*?\)/gi, '');
    cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
    cleaned = cleaned.trim();
    
    console.log("✅ Texto limpio");
    return cleaned;
  };

  const loadLyrics = async () => {
    setLoadingLyrics(true);
    setError("");
    
    try {
      const response = await getLyrics(song.id);
      
      if (response.lyrics) {
        const cleaned = cleanLyricsText(response.lyrics);
        
        if (cleaned && cleaned.length > 20) {
          setLyrics(cleaned);
          setShowLyrics(true);
          console.log("✅ Letras cargadas y limpias");
        } else {
          throw new Error("Las letras están vacías después de limpiar");
        }
      } else {
        throw new Error("No hay letras disponibles");
      }
    } catch (err) {
      console.error("❌ Error al cargar letras:", err);
      setError("Letras no disponibles para esta canción");
      setLyrics("");
    } finally {
      setLoadingLyrics(false);
    }
  };

  const loadTranslation = async (lang) => {
    if (!lyrics) {
      console.log("⚠️ No hay letras para traducir");
      return;
    }

    setTargetLanguage(lang);
    setLoadingTranslation(true);
    setError("");

    try {
      console.log(`🌍 Traduciendo a: ${lang}`);
      const translated = await translateText(lyrics, lang);
      
      if (translated && translated.length > 20) {
        setTranslatedLyrics(translated);
        console.log("✅ Traducción completada");
      } else {
        throw new Error("Traducción vacía o muy corta");
      }
    } catch (err) {
      console.error("❌ Error al traducir:", err);
      setTranslatedLyrics("❌ No se pudo traducir las letras.\n\nIntenta seleccionar otro idioma.");
    } finally {
      setLoadingTranslation(false);
    }
  };

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    if (newLang && lyrics) {
      setTranslatedLyrics("");
      loadTranslation(newLang);
    } else if (!newLang) {
      setTranslatedLyrics("");
    }
  };

  if (!song) return null;

  const embedUrl = streamingUrl 
    ? `https://www.youtube.com/embed/${streamingUrl}?autoplay=1&rel=0` 
    : null;

  return (
    <div className="music-player-overlay fullscreen">
      <div className="music-player-fullscreen">
        
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
              <option value="es">🇪🇸 Traducir a Español</option>
              <option value="en">🇺🇸 Translate to English</option>
              <option value="pt">🇧🇷 Traduzir para Português</option>
              <option value="fr">🇫🇷 Traduire en Français</option>
              <option value="de">🇩🇪 Übersetzen auf Deutsch</option>
              <option value="it">🇮🇹 Traduci in Italiano</option>
            </select>

            <button className="close-fullscreen-btn" onClick={onClose}>
              ✕ Cerrar
            </button>
          </div>
        </header>

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

        <div className="player-fullscreen-content">
          
          <div className="lyrics-column left-column">
            <div className="lyrics-section-fullscreen">
              <h3>📝 Letra Original</h3>
              {loadingLyrics ? (
                <div className="lyrics-loading">
                  <div className="spinner-small"></div>
                  <p>Cargando letras...</p>
                </div>
              ) : lyrics ? (
                <div 
                  className="lyrics-text-fullscreen"
                  ref={originalLyricsRef}
                  onScroll={handleOriginalScroll}
                >
                  {lyrics.split('\n').map((line, index) => (
                    <p key={`original-${index}`} className="lyric-line">
                      {line.trim() || '\u00A0'}
                    </p>
                  ))}
                </div>
              ) : (
                <div className="no-lyrics-message">
                  <p className="no-lyrics-icon">📝</p>
                  <p>Letras no disponibles</p>
                  <small>Intenta con otra canción</small>
                </div>
              )}
            </div>
          </div>

          <div className="lyrics-column right-column">
            <div className="lyrics-section-fullscreen">
              <h3>
                🌍 Letra Traducida 
                {targetLanguage && ` (${getLanguageName(targetLanguage)})`}
              </h3>
              
              {loadingTranslation ? (
                <div className="lyrics-loading">
                  <div className="spinner-small"></div>
                  <p>Traduciendo a {getLanguageName(targetLanguage)}...</p>
                </div>
              ) : translatedLyrics ? (
                <div 
                  className="lyrics-text-fullscreen"
                  ref={translatedLyricsRef}
                  onScroll={handleTranslatedScroll}
                >
                  {translatedLyrics.split('\n').map((line, index) => (
                    <p key={`translated-${index}`} className="lyric-line">
                      {line.trim() || '\u00A0'}
                    </p>
                  ))}
                </div>
              ) : lyrics && !loadingLyrics ? (
                <div className="select-language-prompt">
                  <div className="prompt-icon">🌐</div>
                  <p>Traduciendo automáticamente...</p>
                </div>
              ) : (
                <div className="no-lyrics-message">
                  <p className="no-lyrics-icon">🌍</p>
                  <p>Traducción no disponible</p>
                  <small>Primero deben cargarse las letras originales</small>
                </div>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="player-error-footer">{error}</div>
        )}
      </div>
    </div>
  );
};

const getLanguageName = (code) => {
  const languages = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
  };
  return languages[code] || code.toUpperCase();
};

export default MusicPlayer;