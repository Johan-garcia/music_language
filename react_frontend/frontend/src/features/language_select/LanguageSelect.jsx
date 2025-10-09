import './LanguageSelect.css';

export default function LanguageSelect({ onChange }) {
  return (
    <div className="language-select">
      <label>Idioma: </label>
      <select onChange={(e) => onChange(e.target.value)}>
        <option value="en">Inglés</option>
        <option value="es">Español</option>
        <option value="fr">Francés</option>
      </select>
    </div>
  );
}
