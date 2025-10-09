import './Video.css';

export default function Video({ url }) {
  return (
    <div className="video">
      {url ? (
        <iframe src={url} frameBorder="0" allowFullScreen></iframe>
      ) : (
        <p>Ingresa un enlace para mostrar el video</p>
      )}
    </div>
  );
}
