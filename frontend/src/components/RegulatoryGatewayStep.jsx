import React from 'react';

const RegulatoryGatewayStep = ({ formData, handleChange }) => {
  return (
    <div>
      <h2>Step 1: Regulatory Gateway</h2>
      <p>This form helps determine if your project needs formal planning permission.</p>

      <div>
        <label>
          Wall Height (H) in meters:
          <input
            type="number"
            value={formData.wall_height}
            onChange={handleChange('wall_height')}
            min="0.3"
            max="2.5"
            step="0.1"
          />
        </label>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={formData.is_adjacent_to_highway}
            onChange={handleChange('is_adjacent_to_highway')}
          />
          Is the wall adjacent to a road, footpath, or public right of way?
        </label>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={formData.is_within_3_7m_of_street}
            onChange={handleChange('is_within_3_7m_of_street')}
          />
          Is the wall within 3.7m (12 ft) of a street?
        </label>
      </div>

      <div>
        <label>
          <input
            type="checkbox"
            checked={formData.special_area_check}
            onChange={handleChange('special_area_check')}
            required
          />
          I have confirmed my property is NOT in a Conservation Area, National Park, or Area of Outstanding Natural Beauty, and is not a Listed Building.
        </label>
        <p><small>(A link to the Powys County Council's interactive map will be here)</small></p>
      </div>
    </div>
  );
};

export default RegulatoryGatewayStep;
