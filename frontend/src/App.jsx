import React from 'react';
import Wizard from './components/Wizard';
import './App.css';

function App() {
  return (
    <div className="App">
      <main>
        <Wizard />
      </main>
      <footer className="App-footer">
        <p>
          Disclaimer: This tool is for informational purposes only. Always consult a qualified professional.
        </p>
        <p>
          Regulations last checked: August 2025
        </p>
      </footer>
    </div>
  );
}

export default App;
