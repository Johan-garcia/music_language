import { useState } from "react";
import axios from "axios";

function UrlInput({ onSongData }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert(" Ingresa el nombre de una canción o artista.");
      return;
    }

    try {
      setLoading(true);
      console.log(`🎧 Buscando: ${query}`);

      // 🔹 Realiza la solicitud POST al endpoint correcto
      const response = await axios.post("http://127.0.0.1:8000/api/v1/music/search", {
        query: query,
        limit: 1,
        language: "en" // o "es" según prefieras
      }, {
        headers: {
          "Content-Type": "application/json",
          // Si tu API requiere autenticación:
          // "Authorization": `Bearer ${token}`
        }
      });

      console.log(" Respuesta del backend:", response.data);

      if (onSongData) onSongData(response.data);

    } catch (error) {
      console.error(" Error al conectar con el backend:", error);
      alert("Error al obtener la canción desde el servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="url-input-container">
      <input
        type="text"
        className="url-input"
        placeholder="Escribe una canción o artista..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button
        className="translate-btn"
        onClick={handleSearch}
        disabled={loading}
      >
        {loading ? " Buscando..." : " Buscar Canción"}
      </button>
    </div>
  );
}

export default UrlInput;
