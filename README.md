# LearnSphere-Oracle

A platform for educational tools, including the Match Maker tool for team project recommendations based on MBTI and Felder-Silverman ILS surveys. This AI-driven system generates personalized prompts, Stable Diffusion images, and complementary team matches to enhance collaborative learning.

## Key Features
- **Survey Processing**: Analyzes MBTI (e.g., Extrovert/Introvert) and ILS (e.g., Visual/Verbal) responses.
- **Prompt & Image Generation**: Creates symbolic visuals tailored to learner profiles using Stable Diffusion.
- **Recommendations**: Clusters profiles for similar/complementary partners, promoting balanced teams.
- **Interfaces**: React frontend for surveys and Streamlit for interactive visualizations.
- **Data Augmentation**: Built-in synthetic data generation for robust testing and scalability.

## Getting Started
See [setup.md](docs/setup.md) for installation. Quick start:
1. Clone the repo: `git clone https://github.com/victordeman/LearnSphere-Oracle`
2. Install deps: `pip install -r backend/requirements.txt` & `npm install` (in frontend/)
3. Run: `docker-compose up`
4. Access Streamlit at `localhost:8501` for demo with sample data.

## Roadmap
### Short-Term (Q1 2026)
- **Enhance Backend**: Integrate real Stable Diffusion in `image_generator.py`; add DB storage for prompts/images.
- **Testing Focus**: Leverage synthetic data augmentation in `prompt_generation.py` (e.g., generate 50+ fake profiles via `augment_data()`) for unit/integration tests on MBTI/ILS scoring, clustering, and recommendations.
- **Frontend Polish**: Expand `SurveyForm.js` to full questionnaire; connect to backend API.

### Medium-Term (Q2 2026)
- **API Development**: Add endpoints for real-time matching; implement user feedback loops.
- **Optimization**: GPU fallbacks, NSFW filters; scale synthetic data for stress testing (aim for 1000+ profiles).
- **Deployment**: Cloud hosting (AWS/Heroku) with CI/CD.

### Long-Term (H2 2026+)
- **Expansion**: Integrate other LearnSphere agents (e.g., Oracle, Task Maker).
- **Research Integration**: Update with latest MBTI/ILS studies for better matching accuracy.
- **Community**: Open-source contributions; add user analytics.

# Architecture

## Overview
LearnSphere-Oracle is a modular AI platform for adaptive education, with the Match Maker as the core support system. It processes survey data to generate personalized content and team recommendations, leveraging MBTI for personality matching and ILS for learning styles.

### Components
- **Backend (Python)**: Handles logic in `src/support_systems/match_maker/`:
  - `prompt_generation.py`: Scores MBTI/ILS, integrates preferences, and augments data synthetically.
  - `prompt_generator.py`: Templates detailed Stable Diffusion prompts.
  - `image_pipeline.py`: Generates/clusters images; recommends partners.
  - API endpoints for integration.
- **Frontend (React)**: User input via `SurveyForm.js`; displays results.
- **Streamlit**: Interactive viz in `app.py` for profiles, images, and recs.
- **Data Flow**: Survey → Processing → Prompts → Images → Clustering → Recommendations.
- **Storage**: Configurable DB/Vector store for scalability.
- **Deployment**: Dockerized services (backend, frontend, streamlit).

## Roadmap Integration
The architecture supports iterative development with testing in mind:

### Short-Term Enhancements
- **Synthetic Data for Testing**: Use `augment_data()` in `prompt_generation.py` to create balanced datasets (e.g., mix Sensing/Intuitive profiles). This enables quick iteration on clustering accuracy without real user data—recommend running 100 synthetic runs for validation.
- **Image Pipeline**: Wire full diffusion; test with synthetic prompts for visual relevance.

### Medium-Term
- **Scalability**: Add vector embeddings for faster retrieval; optimize for large synthetic batches.
- **Feedback Loops**: Store user ratings to refine models.

### Long-Term
- **Modularity**: Plug in new agents; AI-driven roadmap updates based on usage data.

For setup, see [setup.md](../setup.md).


Contributions welcome—see [contributing.md](docs/contributing.md)!

MIT License © 2026
