import { useState, useEffect, useRef } from "react";
import { getLyrics } from "../services/musicService";
import "./NowPlaying.css";

const NowPlaying = ({ song, onClose }) => {
  const [lyrics, setLyrics] = useState({ original: "", translated: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  const audioRef = useRef(null);
  const originalLyricsRef = useRef(null);
  const translatedLyricsRef = useRef(null);
  const isSyncing = useRef(false);

  useEffect(() => {
    if (song) {
      loadLyrics();
    }
  }, [song]);

  // Sincronización del scroll entre las dos columnas de letras
  const handleScroll = (sourceRef, targetRef) => {
    if (isSyncing.current) return;

    isSyncing.current = true;

    if (sourceRef.current && targetRef.current) {
      const scrollPercentage =
        sourceRef.current.scrollTop /
        (sourceRef.current.scrollHeight - sourceRef.current.clientHeight);

      targetRef.current.scrollTop =
        scrollPercentage *
        (targetRef.current.scrollHeight - targetRef.current.clientHeight);
    }

    requestAnimationFrame(() => {
      isSyncing.current = false;
    });
  };

  const loadLyrics = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await getLyrics(
        song.id,
        song.language || "es",
        "en"
      );

      setLyrics({
        original: response.original_lyrics || "Letras no disponibles",
        translated: response.translated_lyrics || "Traducción no disponible",
      });
    } catch (err) {
      console.error("Error al cargar letras:", err);
      setError("No se pudieron cargar las letras");
    } finally {
      setLoading(false);
    }
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

  const handleProgressChange = (e) => {
    const newTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (time) => {
    if (isNaN(time)) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  if (!song) return null;

  return (
    <div className="now-playing">
      <div className="now-playing-container">
        {/* Header con información de la canción */}
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
          <button onClick={onClose} className="close-player-btn">
            ✕
          </button>
        </div>

        {/* Reproductor de audio */}
        {song.audio_url ? (
          <div className="audio-player">
            <audio
              ref={audioRef}
              src={song.audio_url}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onEnded={() => setIsPlaying(false)}
            />

            <div className="player-controls">
              <button onClick={togglePlayPause} className="control-btn">
                {isPlaying ? "⏸" : "▶"}
              </button>

              <div className="progress-container">
                <span className="time-display">{formatTime(currentTime)}</span>
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleProgressChange}
                  className="progress-bar"
                />
                <span className="time-display">{formatTime(duration)}</span>
              </div>

              <div className="volume-control">
                <span>🔊</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="volume-slider"
                />
              </div>
            </div>

            <div className="audio-note">
              <p>
                <strong>Nota:</strong> El audio puede no estar disponible para
                todas las canciones
              </p>
            </div>
          </div>
        ) : (
          <div className="no-audio">
            <p>Audio no disponible para esta canción</p>
          </div>
        )}

        {/* Sección de letras sincronizadas */}
        <div className="lyrics-section">
          <div className="lyrics-column">
            <h3>🎵 Letra Original ({song.language?.toUpperCase() || "ES"})</h3>
            {loading ? (
              <div className="lyrics-loading">
                <div className="spinner"></div>
                <p>Cargando letras...</p>
              </div>
            ) : error ? (
              <div className="no-lyrics">{error}</div>
            ) : (
              <div
                ref={originalLyricsRef}
                className="lyrics-text"
                onScroll={() =>
                  handleScroll(originalLyricsRef, translatedLyricsRef)
                }
              >
                {lyrics.original.split("\n").map((line, index) => (
                  <div key={index} className="lyric-line">
                    {line || "\u00A0"}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="lyrics-column">
            <h3>🌍 Traducción (EN)</h3>
            {loading ? (
              <div className="lyrics-loading">
                <div className="spinner"></div>
                <p>Cargando traducción...</p>
              </div>
            ) : error ? (
              <div className="no-lyrics">{error}</div>
            ) : (
              <div
                ref={translatedLyricsRef}
                className="lyrics-text"
                onScroll={() =>
                  handleScroll(translatedLyricsRef, originalLyricsRef)
                }
              >
                {lyrics.translated.split("\n").map((line, index) => (
                  <div key={index} className="lyric-line">
                    {line || "\u00A0"}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="player-error">
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NowPlaying;