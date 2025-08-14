import React from 'react';

const WallAndSoilStep = ({ formData, handleChange, soilTypes, surchargeLoads }) => {
  return (
    <div>
      <h2>Step 2: Wall & Soil Specification</h2>

      <div>
        <label>
          Retained Soil Type:
          <select
            value={formData.soil_type_id || ''}
            onChange={handleChange('soil_type_id')}
            required
          >
            <option value="" disabled>Select soil type...</option>
            {(soilTypes || []).map(type => (
              <option key={type.id} value={type.id}>{type.name}</option>
            ))}
          </select>
        </label>
      </div>

      <div>
        <label>
          Surcharge Load (what is on the land above the wall?):
          <select
            value={formData.surcharge_load_id || ''}
            onChange={handleChange('surcharge_load_id')}
            required
          >
            <option value="" disabled>Select surcharge load...</option>
            {(surchargeLoads || []).map(load => (
              <option key={load.id} value={load.id}>{load.name}</option>
            ))}
          </select>
        </label>
      </div>

       <p><small>Note: Wall Length is not required for the structural calculation per meter, but you would need it for calculating total material quantities later.</small></p>
    </div>
  );
};

export default WallAndSoilStep;
