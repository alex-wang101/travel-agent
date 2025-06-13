# Smart Travel Assistant

A multi-agent system that serves as a travel assistant capable of answering flight status queries and providing historical flight price analysis.

## Overview

This Smart Travel Assistant is built using a multi-agent architecture with three specialized agents:

1. **Inquiry Router Agent**: The "brain" that classifies user queries and routes them to the appropriate specialized agent. Uses LLM-based classification (Gemini API) with fallback to rule-based routing.

2. **Flight Status Agent**: Connects to the AviationStack API to retrieve real-time information about specific flights.

3. **Flight Analytics Agent**: Queries Google BigQuery's public flight dataset to analyze historical flight data and trends.

## Features

- **Real-time Flight Status**: Check the status of any flight by providing its flight number (e.g., "What is the status of flight AA123?").
- **Historical Flight Price Analysis**: Get insights about flight prices between airports (e.g., "What were the cheapest flights from JFK to LAX last year?").
- **LLM-based Query Classification**: Uses Google's Gemini API to intelligently classify user queries.
- **Conversational Memory**: Remembers context from previous queries to handle follow-up questions (e.g., "What about from SFO to DEN?").
- **Complex Analytics**: Can answer questions like "Which day of the week is cheapest to fly from SFO to JFK?".

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- AviationStack API key (get a free key at https://aviationstack.com/)
- Google Cloud account with BigQuery access
- (Optional) Google Gemini API key for LLM-based routing

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/smart-travel-assistant.git
   cd smart-travel-assistant
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file in the project root:
   ```
   AVIATIONSTACK_API_KEY=your_aviationstack_api_key
   GEMINI_API_KEY=your_gemini_api_key (optional)
   ```

4. Authenticate with Google Cloud for BigQuery access:
   ```
   gcloud auth application-default login
   ```

### Usage

Run the main script to start the Smart Travel Assistant:

```
python main.py
```

Follow the prompts to interact with the assistant. You can ask questions like:

- "What is the status of flight AA123?"
- "Show me the cheapest flights from SFO to JFK last year"
- "Which day is cheapest to fly from ORD to LAX?"

Type 'exit' to quit the assistant.

## Sample Interactions

### Example 1: Flight Status Query

```
============================================================
               SMART TRAVEL ASSISTANT
============================================================

Welcome to your Smart Travel Assistant!
You can ask about:
  1. Flight status - information on flight number (e.g., 'What is the status of flight AA123?')
  2. Flight analysis - information on the delay from origin to destination (e.g., 'What is the most on time flight from JFK to LAX?'

Type 'exit' to quit the assistant.



How can I help you? what is the status of flight aa123

Processing your request...
LLM classified as flight status query with flight number: AA123

Result:
Flight AA123 operated by American Airlines
Route: Dallas/Fort Worth International (DFW) to Kahului (OGG)
Status: Active
Scheduled departure: 2025-06-12T11:11:00+00:00
Scheduled arrival: 2025-06-12T14:00:00+00:00
Departure delay: 20 minutes
Departure: Terminal A, Gate A34


How can I help you? 
```

### Example 2: Flight Analytics Query

```
============================================================
               SMART TRAVEL ASSISTANT
============================================================

Welcome to your Smart Travel Assistant!
You can ask about:
  1. Flight status - information on flight number (e.g., 'What is the status of flight AA123?')
  2. Flight analysis - information on the delay from origin to destination (e.g., 'What is the most on time flight from JFK to LAX?'

Type 'exit' to quit the assistant.



How can I help you? what is the most on time flight from jfk to lax

Processing your request...
LLM classified as flight analytics query with origin: jfk, destination: lax

Result:
Based on historical data for flights from JFK to LAX, the airlines with the best on-time performance were:

#1. UA (avg delay: 1.6 min, based on 2037 flights)
#2. AA (avg delay: -1.9 min, based on 3187 flights)
#3. B6 (avg delay: 2.0 min, based on 1669 flights)
#4. VX (avg delay: 2.1 min, based on 1779 flights)
#5. DL (avg delay: -3.8 min, based on 2487 flights)
```


## Architecture Design

The Smart Travel Assistant follows a modular agent-based architecture:

1. **User Query** → The user inputs a natural language query about flights.

2. **Inquiry Router Agent** → Analyzes the query using LLM-based classification (with rule-based fallback) and routes it to the appropriate specialized agent.

3. **Specialized Agents**:
   - **Flight Status Agent** → Calls AviationStack API for real-time flight information.
   - **Flight Analytics Agent** → Queries BigQuery for historical flight data analysis.

4. **Response** → The specialized agent processes the data and returns a human-readable response.

## License

MIT License
