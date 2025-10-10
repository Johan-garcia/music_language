import { useNavigate } from "react-router-dom";
import "./Home.css";

const Home = () => {
  const navigate = useNavigate();

  const goToLyrics = () => navigate("/lyrics");
  const goToArtists = () => navigate("/artists");
  const goToFavorites = () => navigate("/favorites");
  const goToSearch = () => navigate("/search");

  return (
    <div className="home">
      <h2>🎧 Bienvenido a Music Filtering App</h2>
      <p>Explora, busca y disfruta de tu música favorita.</p>

      <div className="home-buttons">
        <button onClick={goToSearch}>Buscar Canción</button>
        <button onClick={goToLyrics}>Letras</button>
        <button onClick={goToArtists}>Artistas</button>
        <button onClick={goToFavorites}>Favoritos</button>
      </div>

      <div className="home-footer">
        <p className="note">
          Sesión iniciada correctamente. Usa los botones para navegar por las secciones.
        </p>
      </div>
    </div>
  );
};

export default Home;
