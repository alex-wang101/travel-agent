import requests
import json

class FlightStatusAgent:
    """Agent responsible for retrieving real-time flight status information.
    
    This agent connects to the AviationStack API to get current information
    about specific flights based on their flight number.
    """
    
    def __init__(self, aviation_api_key):
        """Initialize the FlightStatusAgent with an API key.
        
        Args:
            aviation_api_key: API key for the AviationStack service
        """
        self.aviation_api_key = aviation_api_key
        self.base_url = "http://api.aviationstack.com/v1/flights"
    
    def get_flight_status(self, flight_number):
        """Get the current status of a specific flight.
        
        Args:
            flight_number: The flight number to look up (e.g., 'AA123')
            
        Returns:
            A human-readable string with flight status information
        """
        if not flight_number:
            return "Please provide a valid flight number."
        
        # Extract airline code and flight number
        # Most flight numbers have a 2-letter airline code followed by numbers
        airline_code = ''.join([c for c in flight_number if c.isalpha()]).upper()
        flight_digits = ''.join([c for c in flight_number if c.isdigit()])
        
        # Prepare API request parameters
        params = {
            'access_key': self.aviation_api_key,
            'flight_number': flight_digits,
            'airline_iata': airline_code
        }
        
        try:
            # Make the API request
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                error_code = data['error']['code']
                error_message = data['error']['message']
                return f"API Error {error_code}: {error_message}"
            
            # Process the response
            flights = data.get('data', [])
            
            if not flights:
                return f"Could not find information for flight {flight_number}. Please check the flight number."
            
            # Get the most relevant flight (usually the first one)
            flight = flights[0]
            
            # Extract flight information
            airline = flight.get('airline', {}).get('name', 'Unknown Airline')
            flight_iata = flight.get('flight', {}).get('iata', flight_number)
            departure_airport = flight.get('departure', {}).get('airport', 'Unknown')
            departure_iata = flight.get('departure', {}).get('iata', '')
            arrival_airport = flight.get('arrival', {}).get('airport', 'Unknown')
            arrival_iata = flight.get('arrival', {}).get('iata', '')
            status = flight.get('flight_status', 'Unknown')
            scheduled_departure = flight.get('departure', {}).get('scheduled', 'Unknown')
            scheduled_arrival = flight.get('arrival', {}).get('scheduled', 'Unknown')
            
            # Format departure and arrival information
            departure_info = f"{departure_airport} ({departure_iata})" if departure_iata else departure_airport
            arrival_info = f"{arrival_airport} ({arrival_iata})" if arrival_iata else arrival_airport
            
            # Build the response
            response = f"Flight {flight_iata} operated by {airline}\n"
            response += f"Route: {departure_info} to {arrival_info}\n"
            response += f"Status: {status.capitalize()}\n"
            response += f"Scheduled departure: {scheduled_departure}\n"
            response += f"Scheduled arrival: {scheduled_arrival}\n"
            
            # Add delay information if available
            departure_delay = flight.get('departure', {}).get('delay')
            if departure_delay:
                response += f"Departure delay: {departure_delay} minutes\n"
            
            arrival_delay = flight.get('arrival', {}).get('delay')
            if arrival_delay:
                response += f"Arrival delay: {arrival_delay} minutes\n"
            
            # Add terminal and gate information if available
            departure_terminal = flight.get('departure', {}).get('terminal')
            departure_gate = flight.get('departure', {}).get('gate')
            if departure_terminal or departure_gate:
                terminal_gate = []
                if departure_terminal:
                    terminal_gate.append(f"Terminal {departure_terminal}")
                if departure_gate:
                    terminal_gate.append(f"Gate {departure_gate}")
                response += f"Departure: {', '.join(terminal_gate)}\n"
            
            arrival_terminal = flight.get('arrival', {}).get('terminal')
            arrival_gate = flight.get('arrival', {}).get('gate')
            if arrival_terminal or arrival_gate:
                terminal_gate = []
                if arrival_terminal:
                    terminal_gate.append(f"Terminal {arrival_terminal}")
                if arrival_gate:
                    terminal_gate.append(f"Gate {arrival_gate}")
                response += f"Arrival: {', '.join(terminal_gate)}\n"
            
            return response
            
        except requests.exceptions.RequestException as e:
            return f"Error connecting to flight status API: {str(e)}"
        except json.JSONDecodeError:
            return "Error parsing API response. Please try again later."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
