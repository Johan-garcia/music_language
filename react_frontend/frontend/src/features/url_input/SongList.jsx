// src/features/url_input/SongList.jsx
import React from "react";
import "./UrlInput.css";

const SongList = ({ songs }) => {
  if (!songs.length) return null;

  return (
    <div className="song-list">
      <h3>Resultados de la búsqueda</h3>
      {songs.map((song) => (
        <div key={song.id} className="song-card">
          <img src={song.thumbnail_url} alt={song.title} />
          <div className="song-info">
            <h4>{song.title}</h4>
            <p>{song.artist}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SongList;
