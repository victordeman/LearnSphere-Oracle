import React, { useState } from 'react';

const SurveyForm = () => {
  const [responses, setResponses] = useState({});
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setResponses(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(responses),
    })
      .then(response => response.json())
      .then(data => setResult(data.recommendations))
      .catch(error => console.error('Error:', error));
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          How do you prefer to collaborate?
          <select name="collaboration" onChange={handleChange}>
            <option value="outgoing">Outgoing</option>
            <option value="introspective">Introspective</option>
          </select>
        </label>
        <label>
          How do you process information?
          <select name="info_process" onChange={handleChange}>
            <option value="practical">Practical</option>
            <option value="imaginative">Imaginative</option>
          </select>
        </label>
        <button type="submit">Get Matches</button>
      </form>
      {result && <div>Recommended Partners: {JSON.stringify(result)}</div>}
    </div>
  );
};

export default SurveyForm;
