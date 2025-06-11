import re
import os
import google.generativeai as genai

class InquiryRouterAgent:
    """Agent responsible for routing user queries to the appropriate specialized agent.
    
    This agent uses LLM-based classification to determine whether a query should be handled
    by the Flight Status Agent or the Flight Analytics Agent. It also maintains
    conversational memory to handle follow-up questions.
    """
    
    def __init__(self, flight_status_agent, flight_analytics_agent):
        """Initialize the router agent with references to the specialized agents.
        
        Args:
            flight_status_agent: Instance of FlightStatusAgent
            flight_analytics_agent: Instance of FlightAnalyticsAgent
        """
        self.flight_status_agent = flight_status_agent
        self.flight_analytics_agent = flight_analytics_agent
        
        # Regular expression pattern for flight numbers (fallback)
        # Most airline codes are 2 letters followed by 3-4 digits
        self.flight_number_pattern = r'([A-Z]{2}|[A-Z]\d)\s*\d{1,4}'
        
        # Initialize conversation memory
        self.conversation_memory = {
            "last_query_type": None,  # "flight_status" or "flight_analytics"
            "last_origin": None,      # Origin airport code (e.g., "SFO")
            "last_destination": None,  # Destination airport code (e.g., "JFK")
            "last_context": None,     # Full context of the last query
            "last_flight_number": None # Last flight number queried
        }
        
        # Initialize Gemini API if key is available
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.use_llm = False
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.use_llm = True
                print("LLM-based routing enabled using Gemini API")
            except Exception as e:
                print(f"Failed to initialize Gemini API: {str(e)}")
                print("Falling back to rule-based routing")
    
    def extract_flight_number(self, query):
        """Extract a flight number from the user query if present.
        
        Args:
            query: User's query string
            
        Returns:
            The extracted flight number or None if not found
        """
        # Convert query to uppercase to match the pattern
        uppercase_query = query.upper()
        
        # Search for the flight number pattern
        match = re.search(self.flight_number_pattern, uppercase_query)
        
        if match:
            # Return the matched flight number
            return match.group(0).replace(' ', '')
        
        return None
    
    def classify_intent_with_llm(self, query):
        """Use Gemini to classify the user's intent.
        
        Args:
            query: User's query string
            
        Returns:
            Dict with classification results including intent type and extracted entities
        """
        if not self.use_llm:
            return None
            
        try:
            # Create a prompt for the LLM
            prompt = f"""
            Classify the following travel query into one of two categories:
            1. flight_status - If the query is asking about a specific flight's status, delay, etc.
            2. flight_analytics - If the query is asking about historical flight data, prices, trends, etc.
            
            Also extract any relevant entities:
            - flight_number: The flight number if present (e.g., AA123)
            - origin: The origin airport code if present (e.g., SFO)
            - destination: The destination airport code if present (e.g., JFK)
            
            Query: {query}
            
            Respond in JSON format with the following structure:
            {{"intent": "flight_status OR flight_analytics", "flight_number": "EXTRACTED_NUMBER OR null", "origin": "ORIGIN_CODE OR null", "destination": "DESTINATION_CODE OR null"}}
            """
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            try:
                # Extract the JSON part from the response
                import json
                response_text = response.text
                
                # If the response is wrapped in code blocks, extract just the JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].strip()
                
                # Parse the JSON
                result = json.loads(response_text)
                return result
            except Exception as e:
                print(f"Failed to parse LLM response: {str(e)}")
                print(f"Raw response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error using LLM for classification: {str(e)}")
            return None
    
    def update_memory(self, query, intent_type, flight_number=None, origin=None, destination=None):
        """Update the conversation memory with the current query context.
        
        Args:
            query: The user's query string
            intent_type: The type of intent ("flight_status" or "flight_analytics")
            flight_number: The flight number if present
            origin: The origin airport code if present
            destination: The destination airport code if present
        """
        self.conversation_memory["last_query_type"] = intent_type
        self.conversation_memory["last_context"] = query
        
        if flight_number:
            self.conversation_memory["last_flight_number"] = flight_number
            
        if origin:
            self.conversation_memory["last_origin"] = origin
            
        if destination:
            self.conversation_memory["last_destination"] = destination
    
    def handle_follow_up_query(self, query):
        """Handle follow-up queries by using conversation memory.
        
        Args:
            query: The user's query string
            
        Returns:
            Tuple of (is_follow_up, processed_query) where processed_query
            incorporates context from memory if needed
        """
        # Check for follow-up indicators
        follow_up_indicators = [
            "what about", "how about", "and", "what if", 
            "instead", "also", "another", "different"
        ]
        
        is_follow_up = any(indicator in query.lower() for indicator in follow_up_indicators)
        
        # If this doesn't seem like a follow-up, return the original query
        if not is_follow_up or not self.conversation_memory["last_query_type"]:
            return False, query
        
        # Handle follow-up for flight status queries
        if self.conversation_memory["last_query_type"] == "flight_status":
            # Extract flight number from the follow-up if present
            flight_number = self.extract_flight_number(query)
            
            if not flight_number:
                # If no flight number in follow-up but we have one in memory,
                # this might be a request for more details about the same flight
                if "more" in query.lower() or "details" in query.lower():
                    return True, f"Tell me more about flight {self.conversation_memory['last_flight_number']}"
        
        # Handle follow-up for flight analytics queries
        elif self.conversation_memory["last_query_type"] == "flight_analytics":
            # Extract origin and destination from follow-up
            origin, destination = self.extract_airports(query)
            
            # If we have partial information, fill in from memory
            if origin and not destination and self.conversation_memory["last_destination"]:
                # User specified new origin but kept the same destination
                processed_query = f"Show me flights from {origin} to {self.conversation_memory['last_destination']}"
                return True, processed_query
                
            elif not origin and destination and self.conversation_memory["last_origin"]:
                # User specified new destination but kept the same origin
                processed_query = f"Show me flights from {self.conversation_memory['last_origin']} to {destination}"
                return True, processed_query
                
            elif not origin and not destination:
                # No specific airports mentioned, might be asking for more details
                # about the previous query
                if "cheapest" in query.lower() and self.conversation_memory["last_origin"] and self.conversation_memory["last_destination"]:
                    processed_query = f"What are the cheapest flights from {self.conversation_memory['last_origin']} to {self.conversation_memory['last_destination']}?"
                    return True, processed_query
                elif "day" in query.lower() and self.conversation_memory["last_origin"] and self.conversation_memory["last_destination"]:
                    processed_query = f"Which day is cheapest to fly from {self.conversation_memory['last_origin']} to {self.conversation_memory['last_destination']}?"
                    return True, processed_query
        
        # If we couldn't enhance the follow-up, return the original
        return is_follow_up, query
    
    def route_query(self, query):
        """Route the user query to the appropriate specialized agent.
        
        Args:
            query: User's query string
            
        Returns:
            Response from the appropriate specialized agent
        """
        # Check if this is a follow-up query
        is_follow_up, processed_query = self.handle_follow_up_query(query)
        if is_follow_up:
            print(f"Detected follow-up query. Enhanced query: '{processed_query}'")
            query = processed_query
        
        # Try LLM-based classification first
        if self.use_llm:
            classification = self.classify_intent_with_llm(query)
            
            if classification:
                intent_type = classification.get("intent")
                flight_number = classification.get("flight_number")
                origin = classification.get("origin")
                destination = classification.get("destination")
                
                # Update conversation memory
                self.update_memory(query, intent_type, flight_number, origin, destination)
                
                if intent_type == "flight_status":
                    print(f"LLM classified as flight status query with flight number: {flight_number}")
                    return self.flight_status_agent.get_flight_status(flight_number)
                elif intent_type == "flight_analytics":
                    print(f"LLM classified as flight analytics query with origin: {origin}, destination: {destination}")
                    return self.flight_analytics_agent.analyze_flight_data(query)
        
        # Fallback to rule-based classification
        flight_number = self.flight_status_agent.extract_flight_number(query)
        origin, destination = self.flight_analytics_agent.extract_airports(query)
        
        # If a flight number is found, route to the Flight Status Agent
        if flight_number:
            print(f"Rule-based routing to Flight Status Agent with flight number: {flight_number}")
            self.update_memory(query, "flight_status", flight_number)
            return self.flight_status_agent.get_flight_status(flight_number)
        
        # Otherwise, route to the Flight Analytics Agent
        else:
            print(f"Rule-based routing to Flight Analytics Agent with origin: {origin}, destination: {destination}")
            self.update_memory(query, "flight_analytics", None, origin, destination)
            return self.flight_analytics_agent.analyze_flight_data(query)
