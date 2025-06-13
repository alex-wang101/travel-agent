# agents/init.py
from dotenv import load_dotenv
import os
from .flight_status_agent import FlightStatusAgent
from .flight_analytics_agent import FlightAnalyticsAgent
from .route_agent import InquiryRouterAgent

# Load environment variables once
load_dotenv()

# Get API keys
aviation_api_key = os.getenv("AVIATIONSTACK_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")


# Initialize agents once
flight_status_agent = FlightStatusAgent(aviation_api_key)
flight_analytics_agent = FlightAnalyticsAgent()

inquiry_router = InquiryRouterAgent(flight_status_agent, flight_analytics_agent)

