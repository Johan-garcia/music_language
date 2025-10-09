import { useState } from "react";
import Header from "./features/header/Header";
import LanguageSelector from "./features/language_select/LanguageSelect";
import Lyrics from "./features/lyrics/Lyrics";
import Player from "./features/player/Player";
import UrlInput from "./features/url_input/UrlInput";
import Video from "./features/video/Video";
import "./App.css";

function App() {
  // Estado global compartido
  const [songData, setSongData] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("es");
  const [isPlaying, setIsPlaying] = useState(false);

  // Función para manejar datos de la canción obtenidos desde UrlInput.jsx
  const handleSongData = (data) => {
    setSongData(data);
  };

  // Alternar reproducción
  const handleTogglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="app-container">
      {/* Encabezado principal */}
      <Header />

      {/* Selector de idioma */}
      <LanguageSelector
        selectedLanguage={selectedLanguage}
        onChange={setSelectedLanguage}
      />

      {/* Campo para pegar la URL y buscar canción */}
      <UrlInput
        onSongData={handleSongData}
        selectedLanguage={selectedLanguage}
      />

      {/* Reproductor de música/video */}
      <Player isPlaying={isPlaying} onTogglePlay={handleTogglePlay} />

      {/* Muestra la letra original y traducida */}
      <Lyrics songData={songData} />

      {/* (Opcional) Componente de video, si lo usarás */}
      <Video videoId={songData?.videoId} isPlaying={isPlaying} />
    </div>
  );
}

export default App;
