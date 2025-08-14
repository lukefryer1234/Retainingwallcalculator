import React from 'react';

const ResultsStep = ({ results, error }) => {
  if (error) {
    return <div style={{ color: 'red' }}>Error: {error}</div>;
  }

  if (!results) {
    return <div>Loading results...</div>;
  }

  const { regulatory_gateway, engineering_design } = results;

  return (
    <div>
      <h2>Step 3: Your Results</h2>

      <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px' }}>
        <h3>Regulatory Check</h3>
        {regulatory_gateway.map((flag, index) => (
          <div key={index} style={{ color: flag.level === 'RED' ? 'red' : (flag.level === 'ORANGE' ? 'orange' : 'green') }}>
            <strong>{flag.level}:</strong> {flag.message}
          </div>
        ))}
      </div>

      {engineering_design && engineering_design.status === 'OK' && (
        <div style={{ border: '1px solid #ccc', padding: '10px' }}>
          <h3>Engineering Design Specifications (per meter length)</h3>
          <ul>
            {Object.entries(engineering_design.design_specifications).map(([key, value]) => (
              <li key={key}><strong>{key.replace(/_/g, ' ')}:</strong> {value}</li>
            ))}
          </ul>
           <h4>Calculated Safety Factors:</h4>
           <ul>
            <li>Overturning: {engineering_design.calculations.safety_factor_overturning} (Required: {'>='} {engineering_design.required_sf.overturning})</li>
            <li>Sliding: {engineering_design.calculations.safety_factor_sliding} (Required: {'>='} {engineering_design.required_sf.sliding})</li>
            <li>Bearing Pressure: {engineering_design.calculations.max_bearing_pressure_kPa} kPa (Max allowable: {engineering_design.required_sf.bearing_capacity_kPa} kPa)</li>
           </ul>
        </div>
      )}

      {engineering_design && engineering_design.status === 'FAIL' && (
        <div style={{ color: 'red', border: '1px solid red', padding: '10px' }}>
            <h3>Design Failed</h3>
            <p>The provided wall dimensions and conditions did not meet the required safety factors. Please consult a structural engineer.</p>
             <h4>Calculated Safety Factors:</h4>
           <ul>
            <li>Overturning: {engineering_design.calculations.safety_factor_overturning} (Required: {'>='} {engineering_design.required_sf.overturning})</li>
            <li>Sliding: {engineering_design.calculations.safety_factor_sliding} (Required: {'>='} {engineering_design.required_sf.sliding})</li>
            <li>Bearing Pressure: {engineering_design.calculations.max_bearing_pressure_kPa} kPa (Max allowable: {engineering_design.required_sf.bearing_capacity_kPa} kPa)</li>
           </ul>
        </div>
      )}
    </div>
  );
};

export default ResultsStep;
