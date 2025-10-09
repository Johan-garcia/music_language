import './Player.css';

export default function Player({ videoUrl }) {
  if (!videoUrl) return null;

  return (
    <div className="player">
      <iframe
        src={videoUrl}
        title="YouTube player"
        frameBorder="0"
        allowFullScreen
      ></iframe>
    </div>
  );
}
