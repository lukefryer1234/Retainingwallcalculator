import React, { useState, useEffect } from 'react';
import RegulatoryGatewayStep from './RegulatoryGatewayStep';
import WallAndSoilStep from './WallAndSoilStep';
import ResultsStep from './ResultsStep';
import { getSoilTypes, getSurchargeLoads, postCalculation } from '../api';

const Wizard = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    wall_height: 1.0,
    is_adjacent_to_highway: false,
    is_within_3_7m_of_street: false,
    special_area_check: false,
    soil_type_id: '',
    surcharge_load_id: '',
  });

  const [soilTypes, setSoilTypes] = useState([]);
  const [surchargeLoads, setSurchargeLoads] = useState([]);

  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch choice data when the component mounts
    const fetchChoices = async () => {
      try {
        const soilTypesRes = await getSoilTypes();
        setSoilTypes(soilTypesRes.data);

        const surchargeLoadsRes = await getSurchargeLoads();
        setSurchargeLoads(surchargeLoadsRes.data);
      } catch (err) {
        setError('Failed to load initial data. Please check the backend connection.');
        console.error(err);
      }
    };
    fetchChoices();
  }, []);

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleChange = (input) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [input]: value });
  };

  const handleSubmit = async () => {
    setError(null);
    setResults(null);
    try {
      const response = await postCalculation(formData);
      setResults(response.data);
      setStep(3); // Move to results step
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unknown error occurred.';
      setError(`Calculation failed: ${JSON.stringify(errorMessage)}`);
      console.error(err);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return <RegulatoryGatewayStep formData={formData} handleChange={handleChange} />;
      case 2:
        return <WallAndSoilStep formData={formData} handleChange={handleChange} soilTypes={soilTypes} surchargeLoads={surchargeLoads} />;
      case 3:
        return <ResultsStep results={results} error={error} />;
      default:
        // Allow restarting the wizard
        setStep(1);
        setResults(null);
        return null;
    }
  };

  return (
    <div>
      <h1>Retaining Wall Wizard</h1>
      {renderStep()}
      <div style={{ marginTop: '20px' }}>
        {step > 1 && step < 3 && <button onClick={prevStep}>Back</button>}
        {step === 1 && <button onClick={nextStep} disabled={!formData.special_area_check}>Next</button>}
        {step === 2 && <button onClick={handleSubmit} disabled={!formData.soil_type_id || !formData.surcharge_load_id}>Calculate</button>}
        {step === 3 && <button onClick={() => setStep(1)}>Start Over</button>}
      </div>
       {error && <div style={{ color: 'red', marginTop: '10px' }}><strong>Error:</strong> {error}</div>}
    </div>
  );
};

export default Wizard;
