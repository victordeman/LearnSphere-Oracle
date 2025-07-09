import React from 'react';
import SurveyForm from './SurveyForm';
import './styles.css';

const MatchMaker = () => {
  return (
    <div className="match-maker">
      <h1>Match Maker</h1>
      <p>Find your perfect team partners based on your collaboration style and learning approach!</p>
      <SurveyForm />
    </div>
  );
};

export default MatchMaker;
