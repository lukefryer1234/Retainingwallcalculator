import React, { useState, useEffect } from 'react';
import { getSoilTypes, getWallMaterials, postCalculation } from '../api';
import ResultsDisplay from './ResultsDisplay'; // Import the new component
import './Calculator.css';

const EurocodeCalculator = () => {
  const [formData, setFormData] = useState({
    retained_height: 1.5,
    wall_material_id: '',
    stem_thickness: 0.3,
    base_width: 0.9,
    base_thickness: 0.3,
    toe_length: 0.3,
    heel_length: 0.3,
    retained_soil_type_id: '',
    foundation_soil_type_id: '',
    ground_slope_angle: 0,
    water_table_height: 0,
    surcharge_load: 10.0,
  });

  const [soilTypes, setSoilTypes] = useState([]);
  const [wallMaterials, setWallMaterials] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const soilRes = await getSoilTypes();
        setSoilTypes(soilRes.data);
        const materialRes = await getWallMaterials();
        setWallMaterials(materialRes.data);

        if (soilRes.data.length > 0 && materialRes.data.length > 0) {
          setFormData(prev => ({
            ...prev,
            retained_soil_type_id: soilRes.data[1].id,
            foundation_soil_type_id: soilRes.data[1].id,
            wall_material_id: materialRes.data[0].id,
          }));
        }
      } catch (err) {
        setError('Failed to load initial data. Please refresh the page.');
      }
    };
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const response = await postCalculation(formData);
      setResults(response.data);
    } catch (err) {
      if (err.response && err.response.data) {
        const errorData = err.response.data;
        const errorMessages = Object.keys(errorData).map(key => `${key}: ${Array.isArray(errorData[key]) ? errorData[key].join(', ') : errorData[key]}`).join('; ');
        setError(`Calculation failed: ${errorMessages}`);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    const parsedValue = type === 'number' && value !== '' ? parseFloat(value) : value;
    setFormData(prev => ({ ...prev, [name]: parsedValue }));
  };

  return (
    <div className="calculator-container">
      <h1>Eurocode 7 Retaining Wall Calculator</h1>
      <form onSubmit={handleSubmit} className="calculator-form">
        <div className="form-section">
          <h2>Wall Geometry</h2>
          <div className="form-grid">
            <label>Retained Height (m):</label>
            <input type="number" name="retained_height" value={formData.retained_height} onChange={handleChange} step="0.1" required />
            <label>Wall Material:</label>
            <select name="wall_material_id" value={formData.wall_material_id} onChange={handleChange} required>
              <option value="">Select Material...</option>
              {wallMaterials.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
            <label>Stem Thickness (m):</label>
            <input type="number" name="stem_thickness" value={formData.stem_thickness} onChange={handleChange} step="0.01" required />
            <label>Base Width (m):</label>
            <input type="number" name="base_width" value={formData.base_width} onChange={handleChange} step="0.1" required />
            <label>Base Thickness (m):</label>
            <input type="number" name="base_thickness" value={formData.base_thickness} onChange={handleChange} step="0.1" required />
            <label>Toe Length (m):</label>
            <input type="number" name="toe_length" value={formData.toe_length} onChange={handleChange} step="0.1" required />
            <label>Heel Length (m):</label>
            <input type="number" name="heel_length" value={formData.heel_length} onChange={handleChange} step="0.1" required />
          </div>
        </div>
        <div className="form-section">
          <h2>Ground Conditions</h2>
          <div className="form-grid">
            <label>Retained Soil Type:</label>
            <select name="retained_soil_type_id" value={formData.retained_soil_type_id} onChange={handleChange} required>
              <option value="">Select Soil...</option>
              {soilTypes.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <label>Foundation Soil Type:</label>
            <select name="foundation_soil_type_id" value={formData.foundation_soil_type_id} onChange={handleChange} required>
              <option value="">Select Soil...</option>
              {soilTypes.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <label>Ground Slope Behind Wall (°):</label>
            <input type="number" name="ground_slope_angle" value={formData.ground_slope_angle} onChange={handleChange} required />
            <label>Water Table Height from Base (m):</label>
            <input type="number" name="water_table_height" value={formData.water_table_height} onChange={handleChange} step="0.1" required />
          </div>
        </div>
        <div className="form-section">
          <h2>Surcharge Load</h2>
          <div className="form-grid">
            <label>Uniform Surcharge (kPa):</label>
            <input type="number" name="surcharge_load" value={formData.surcharge_load} onChange={handleChange} required />
          </div>
        </div>
        <button type="submit" disabled={loading} className="calculate-button">
          {loading ? 'Calculating...' : 'Calculate'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {results && <ResultsDisplay results={results} />}
    </div>
  );
};

export default EurocodeCalculator;
