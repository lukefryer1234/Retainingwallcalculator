import React from 'react';
import './ResultsDisplay.css';

const CheckRow = ({ label, value, status }) => (
  <div className="check-row">
    <span>{label}:</span>
    <span className="value">{value}</span>
    <span className={`status ${status ? 'pass' : 'fail'}`}>{status ? '✔ PASS' : '✖ FAIL'}</span>
  </div>
);

const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const { overall_status, results_DA1_1, results_DA1_2, warnings } = results;

  return (
    <div className="results-container">
      <div className={`overall-status ${overall_status.toLowerCase()}`}>
        <h2>Overall Design Status: {overall_status}</h2>
      </div>

      <div className="results-section">
        <h3>Design Approach 1, Combination 1 (STR)</h3>
        <CheckRow label="Overturning Stability" value={`Mr = ${results_DA1_1.restoring_moment_d} kNm/m, Mo = ${results_DA1_1.overturning_moment_d} kNm/m`} status={results_DA1_1.overturning_ok} />
        <CheckRow label="Sliding Stability" value={`Fr = ${results_DA1_1.resisting_force_d} kN/m, Fs = ${results_DA1_1.sliding_force_d} kN/m`} status={results_DA1_1.sliding_ok} />
        <CheckRow label="Bearing Pressure" value={`q_max = ${results_DA1_1.max_bearing_pressure_d} kPa`} status={results_DA1_1.bearing_ok} />
      </div>

      <div className="results-section">
        <h3>Design Approach 1, Combination 2 (GEO)</h3>
        <CheckRow label="Overturning Stability" value={`Mr = ${results_DA1_2.restoring_moment_d} kNm/m, Mo = ${results_DA1_2.overturning_moment_d} kNm/m`} status={results_DA1_2.overturning_ok} />
        <CheckRow label="Sliding Stability" value={`Fr = ${results_DA1_2.resisting_force_d} kN/m, Fs = ${results_DA1_2.sliding_force_d} kN/m`} status={results_DA1_2.sliding_ok} />
        <CheckRow label="Bearing Pressure" value={`q_max = ${results_DA1_2.max_bearing_pressure_d} kPa`} status={results_DA1_2.bearing_ok} />
      </div>

      {warnings && warnings.length > 0 && (
        <div className="warnings-section">
          <h3>Warnings & Notes</h3>
          <ul>
            {warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;
