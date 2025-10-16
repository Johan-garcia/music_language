import { useState, useEffect, useRef } from "react";
import { getLyrics } from "../services/musicService";
import { translateText } from "../services/translationService";
import "./NowPlaying.css";

const NowPlaying = ({ song, onClose, targetLanguage = "es" }) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [originalLyrics, setOriginalLyrics] = useState("");
  const [translatedLyrics, setTranslatedLyrics] = useState("");
  const [loadingLyrics, setLoadingLyrics] = useState(false);
  const [loadingTranslation, setLoadingTranslation] = useState(false);
  const [error, setError] = useState("");
  const [audioUrl, setAudioUrl] = useState("");

  useEffect(() => {
    if (song) {
      loadAudioUrl();
      loadLyricsData();
    }
  }, [song]);

  const loadAudioUrl = () => {
    // Construir URL de audio desde YouTube
    if (song.youtube_id) {
      // Usaremos un iframe de YouTube en modo audio
      setAudioUrl(`https://www.youtube.com/embed/${song.youtube_id}?autoplay=1&controls=0&enablejsapi=1`);
    } else {
      setError("No hay audio disponible para esta canción");
    }
  };

  const loadLyricsData = async () => {
    setLoadingLyrics(true);
    setError("");

    try {
      const response = await getLyrics(song.id);
      const lyrics = response.lyrics;
      
      // Limpiar las letras (remover metadata)
      const cleanedLyrics = cleanLyricsText(lyrics);
      setOriginalLyrics(cleanedLyrics);

      // Traducir letras
      setLoadingTranslation(true);
      try {
        const translated = await translateText(cleanedLyrics, targetLanguage);
        setTranslatedLyrics(translated);
      } catch (err) {
        console.error("Error al traducir:", err);
        setTranslatedLyrics("Traducción no disponible");
      } finally {
        setLoadingTranslation(false);
      }

    } catch (err) {
      console.error("Error al cargar letras:", err);
      setError("Letras no disponibles para esta canción");
    } finally {
      setLoadingLyrics(false);
    }
  };

  const cleanLyricsText = (text) => {
    // Remover encabezados como "🎵 Song by Artist"
    let cleaned = text.replace(/🎵.*?\n\n/g, '');
    // Remover fuentes como "[Source: ...]"
    cleaned = cleaned.replace(/\[Source:.*?\]/g, '');
    // Remover líneas de metadata
    cleaned = cleaned.replace(/\(Thanks to.*?\)/g, '');
    return cleaned.trim();
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e) => {
    const seekTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="now-playing">
      <div className="now-playing-container">
        
        {/* Header con info de la canción */}
        <div className="song-header">
          <div className="song-artwork">
            {song.thumbnail_url ? (
              <img src={song.thumbnail_url} alt={song.title} />
            ) : (
              <div className="no-artwork">🎵</div>
            )}
          </div>
          <div className="song-info">
            <h2>{song.title}</h2>
            <p>{song.artist}</p>
          </div>
          <button className="close-player-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Reproductor de audio */}
        <div className="audio-player">
          {song.youtube_id ? (
            <>
              {/* Iframe oculto de YouTube para reproducir audio */}
              <iframe
                ref={audioRef}
                style={{ display: 'none' }}
                src={audioUrl}
                allow="autoplay"
              />
              
              {/* Controles personalizados */}
              <div className="player-controls">
                <button className="control-btn play-btn" onClick={togglePlayPause}>
                  {isPlaying ? "⏸️" : "▶️"}
                </button>

                <div className="progress-container">
                  <span className="time-display">{formatTime(currentTime)}</span>
                  <input
                    type="range"
                    className="progress-bar"
                    min="0"
                    max={duration || 0}
                    value={currentTime}
                    onChange={handleSeek}
                  />
                  <span className="time-display">{formatTime(duration)}</span>
                </div>

                <div className="volume-control">
                  <span>🔊</span>
                  <input
                    type="range"
                    className="volume-slider"
                    min="0"
                    max="1"
                    step="0.1"
                    value={volume}
                    onChange={handleVolumeChange}
                  />
                </div>
              </div>

              {/* Nota: El iframe de YouTube no permite control directo, 
                  usaremos un reproductor alternativo */}
              <div className="audio-note">
                <p>⚠️ Nota: Reproduciendo desde YouTube. Usa los controles del reproductor integrado.</p>
                <iframe
                  width="100%"
                  height="80"
                  src={`https://www.youtube.com/embed/${song.youtube_id}?autoplay=1`}
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  style={{ borderRadius: '10px', marginTop: '10px' }}
                ></iframe>
              </div>
            </>
          ) : (
            <div className="no-audio">
              <p>⚠️ Audio no disponible para esta canción</p>
            </div>
          )}
        </div>

        {/* Sección de letras */}
        <div className="lyrics-section">
          <div className="lyrics-column">
            <h3>📝 Letra Original</h3>
            {loadingLyrics ? (
              <div className="lyrics-loading">
                <div className="spinner"></div>
                <p>Cargando letras...</p>
              </div>
            ) : originalLyrics ? (
              <div className="lyrics-text">
                {originalLyrics.split('\n').map((line, index) => (
                  <p key={index} className="lyric-line">
                    {line.trim() || '\u00A0'}
                  </p>
                ))}
              </div>
            ) : (
              <p className="no-lyrics">Letras no disponibles</p>
            )}
          </div>

          <div className="lyrics-column">
            <h3>🌍 Letra Traducida ({targetLanguage.toUpperCase()})</h3>
            {loadingTranslation ? (
              <div className="lyrics-loading">
                <div className="spinner"></div>
                <p>Traduciendo...</p>
              </div>
            ) : translatedLyrics ? (
              <div className="lyrics-text">
                {translatedLyrics.split('\n').map((line, index) => (
                  <p key={index} className="lyric-line">
                    {line.trim() || '\u00A0'}
                  </p>
                ))}
              </div>
            ) : (
              <p className="no-lyrics">Traducción no disponible</p>
            )}
          </div>
        </div>

        {error && (
          <div className="player-error">{error}</div>
        )}
      </div>
    </div>
  );
};

export default NowPlaying;