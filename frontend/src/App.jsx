import React from 'react';
import EurocodeCalculator from './components/EurocodeCalculator';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Retaining Wall Design Calculator</h1>
      </header>
      <main>
        <EurocodeCalculator />
      </main>
      <footer className="App-footer">
        <p>
          Disclaimer: This tool is for preliminary design and informational purposes only.
          All designs must be verified by a qualified structural or geotechnical engineer before construction.
        </p>
      </footer>
    </div>
  );
}

export default App;
