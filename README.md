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
How can I help you? What is the status of flight AA100?

Processing your request...
Routing to Flight Status Agent with flight number: AA100

Result:
Flight AA100 operated by American Airlines
Route: Chicago (ORD) to London (LHR)
Status: Scheduled
Scheduled departure: 2025-06-10T21:40:00+00:00
Scheduled arrival: 2025-06-11T11:20:00+00:00
Departure: Terminal 3, Gate K19
```

### Example 2: Flight Analytics Query

```
How can I help you? What were the cheapest flights from SFO to JFK in 2022?

Processing your request...
Routing to Flight Analytics Agent

Result:
Based on historical data for flights from SFO to JFK in 2022:
The cheapest fare found was $150.00.
The average fare was $320.75.
The main carriers were: B6, DL, UA.

Top 5 cheapest flights:
1. $150.00 - B6 615 on 2022-02-15
2. $165.50 - B6 2315 on 2022-03-22
3. $172.25 - DL 1234 on 2022-01-18
4. $189.99 - UA 2078 on 2022-04-05
5. $210.50 - B6 1515 on 2022-02-28
```

### Example 3: Follow-up Query with Memory

```
How can I help you? What about from LAX to ORD?

Processing your request...
Detected follow-up query. Enhanced query: 'Show me flights from LAX to ORD'
Routing to Flight Analytics Agent

Result:
Based on historical data for flights from LAX to ORD in 2022:
The cheapest fare found was $135.75.
The average fare was $285.50.
The main carriers were: AA, UA, NK.

Top 5 cheapest flights:
1. $135.75 - NK 955 on 2022-05-10
2. $142.25 - AA 1288 on 2022-03-15
3. $155.00 - UA 2121 on 2022-02-22
4. $168.50 - AA 2500 on 2022-06-07
5. $175.25 - UA 1777 on 2022-04-19
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
