import './Lyrics.css';

export default function Lyrics({ text }) {
  return (
    <div className="lyrics">
      <h2>Letra</h2>
      <p>{text || 'Aún no hay letra disponible.'}</p>
    </div>
  );
}
