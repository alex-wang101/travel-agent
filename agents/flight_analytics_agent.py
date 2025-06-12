import re
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import requests
import os
from dotenv import load_dotenv
from amadeus import Client
import logging

load_dotenv()
amadeus = Client(
    client_id = os.getenv("AMADEUS_API_KEY"),
    client_secret = os.getenv("AMADEUS_API_SECRET")
)

class FlightAnalyticsAgent:
    def __init__(self, amadeus_api_key: str = None, amadeus_api_secret: str = None):
        """
        Initialize the FlightAnalyticsAgent with Amadeus API.
        
        Args:
            amadeus_api_key: Your Amadeus API key (optional)
            amadeus_api_secret: Your Amadeus API secret (optional)
        """
        # Amadeus configuration
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.amadeus_api_key = amadeus_api_key
        self.amadeus_api_secret = amadeus_api_secret
        self.amadeus_base_url = "https://test.api.amadeus.com"
        self.amadeus_access_token = None
        self.token_expires_at = None
        
        self.session = requests.Session()
    
        # Dictionary mapping common airport names to their IATA codes
        self.airport_mapping = {
            # US Airports
            'JFK': 'JFK', 'JOHN F KENNEDY': 'JFK', 'KENNEDY': 'JFK', 'NEW YORK JFK': 'JFK',
            'LAX': 'LAX', 'LOS ANGELES': 'LAX', 'LOS ANGELES INTERNATIONAL': 'LAX',
            'ORD': 'ORD', 'CHICAGO': 'ORD', 'CHICAGO OHARE': 'ORD', "O'HARE": 'ORD',
            'ATL': 'ATL', 'ATLANTA': 'ATL', 'HARTSFIELD': 'ATL', 'HARTSFIELD JACKSON': 'ATL',
            'DFW': 'DFW', 'DALLAS': 'DFW', 'DALLAS FORT WORTH': 'DFW',
            'DEN': 'DEN', 'DENVER': 'DEN', 'DENVER INTERNATIONAL': 'DEN',
            'SFO': 'SFO', 'SAN FRANCISCO': 'SFO',
            'SEA': 'SEA', 'SEATTLE': 'SEA', 'SEATAC': 'SEA',
            'MIA': 'MIA', 'MIAMI': 'MIA',
            'BOS': 'BOS', 'BOSTON': 'BOS', 'LOGAN': 'BOS',
            'LGA': 'LGA', 'LA GUARDIA': 'LGA', 'LAGUARDIA': 'LGA',
            'EWR': 'EWR', 'NEWARK': 'EWR',
            'IAD': 'IAD', 'DULLES': 'IAD', 'WASHINGTON DULLES': 'IAD',
            'DCA': 'DCA', 'REAGAN': 'DCA', 'RONALD REAGAN': 'DCA',
            'PHX': 'PHX', 'PHOENIX': 'PHX',
            'IAH': 'IAH', 'HOUSTON': 'IAH',
            'MCO': 'MCO', 'ORLANDO': 'MCO',
            'LAS': 'LAS', 'LAS VEGAS': 'LAS',
            'MSP': 'MSP', 'MINNEAPOLIS': 'MSP', 'MINNEAPOLIS ST PAUL': 'MSP',
            'DTW': 'DTW', 'DETROIT': 'DTW',
            'PHL': 'PHL', 'PHILADELPHIA': 'PHL',
            'CLT': 'CLT', 'CHARLOTTE': 'CLT',
            'SAN': 'SAN', 'SAN DIEGO': 'SAN',
            'PDX': 'PDX', 'PORTLAND': 'PDX',
            
            # International Airports
            'LHR': 'LHR', 'LONDON HEATHROW': 'LHR', 'HEATHROW': 'LHR',
            'CDG': 'CDG', 'PARIS': 'CDG', 'CHARLES DE GAULLE': 'CDG',
            'FRA': 'FRA', 'FRANKFURT': 'FRA',
            'AMS': 'AMS', 'AMSTERDAM': 'AMS', 'SCHIPHOL': 'AMS',
            'HKG': 'HKG', 'HONG KONG': 'HKG',
            'SYD': 'SYD', 'SYDNEY': 'SYD',
            'NRT': 'NRT', 'TOKYO': 'NRT', 'NARITA': 'NRT',
            'YYZ': 'YYZ', 'TORONTO': 'YYZ',
            'MEX': 'MEX', 'MEXICO CITY': 'MEX',
            'DXB': 'DXB', 'DUBAI': 'DXB'
        }
        
        # Initialize Amadeus access token if credentials provided
        if self.amadeus_api_key and self.amadeus_api_secret:
            self.get_amadeus_access_token()
        
        available_apis = []
        if amadeus_api_key and amadeus_api_secret:
            available_apis.append("Amadeus")
        
        print(f"FlightAnalyticsAgent initialized with: {', '.join(available_apis) if available_apis else 'No APIs configured'}")
    
    def get_amadeus_access_token(self) -> bool:
        """
        Get access token from Amadeus API using OAuth2.
        
        Returns:
            True if token obtained successfully, False otherwise
        """
        # Check if we have a valid token
        if (self.amadeus_access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at - timedelta(minutes=5)):
            return True
        
        url = f"{self.amadeus_base_url}/v1/security/oauth2/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.amadeus_api_key,
            'client_secret': self.amadeus_api_secret
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.amadeus_access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 1799)  # Default to ~30 minutes
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"Amadeus access token obtained, expires at: {self.token_expires_at}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to get Amadeus access token: {str(e)}")
            return False
        except json.JSONDecodeError as e:
            print(f"Failed to parse Amadeus token response: {str(e)}")
            return False
    
    def _make_amadeus_request(self, endpoint: str, method: str = 'GET', 
                             params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """
        Make a request to the Amadeus API.
        
        Args:
            endpoint: API endpoint (e.g., 'v2/shopping/flight-offers')
            method: HTTP method ('GET' or 'POST')
            params: URL parameters for GET requests
            data: JSON data for POST requests
            
        Returns:
            JSON response data or None if error
        """
        if not self.amadeus_api_key or not self.amadeus_api_secret:
            print("Amadeus API credentials not provided")
            return None
        
        # Ensure we have a valid access token
        if not self.get_amadeus_access_token():
            return None
        
        url = f"{self.amadeus_base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.amadeus_access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            else:
                response = self.session.get(url, headers=headers, params=params, timeout=30)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Amadeus API request failed: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse Amadeus API response: {str(e)}")
            return None
    
    def extract_airports(self, query: str) -> Tuple[str, str]:
        """
        Extract origin and destination airport codes from the query.
        If not found, defaults to JFK and LAX.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (origin, destination) airport codes
        """
        # First try to find exact IATA codes in the query
        airports = re.findall(r'\b([A-Z]{3})\b', query)
        
        # Filter out common words that might be mistaken for airport codes
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'NOT', 'BUT', 'ONE', 'TWO', 'WHO', 'HOW', 'WHY'}
        airports = [code for code in airports if code not in common_words]
        
        if len(airports) >= 2:
            print(f"Found airport codes in query: {airports[0]} and {airports[1]}")
            return airports[0], airports[1]
        
        # If we couldn't find airport codes, look for airport names in our mapping
        found_airports = []
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Look for each airport name in the query
        for airport_name, code in self.airport_mapping.items():
            # Skip very short airport names to avoid false matches
            if len(airport_name) <= 3:
                continue
                
            # Check if this airport name is in the query
            if airport_name.lower() in query_lower:
                found_airports.append(code)
                print(f"Found airport in query: {airport_name} ({code})")
                if len(found_airports) >= 2:
                    break
        
        # If we found at least two airports, use them as origin and destination
        if len(found_airports) >= 2:
            print(f"Using found airports: {found_airports[0]} and {found_airports[1]}")
            return found_airports[0], found_airports[1]
        
        # Default to JFK and LAX
        print("Could not find airports in query, defaulting to JFK and LAX")
        return "Cloud not find airports in query", "defaulting to JFK and LAX"
    
    def extract_date_range(self, query: str) -> Tuple[str, str]:
        """Extract date range from the query.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format
        """
        # Check for specific date patterns
        date_pattern = r'\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}/\d{1,2}/\d{4})\b'
        dates = re.findall(date_pattern, query)
        
        if dates:
            # Convert to standard format if needed
            start_date = dates[0]
            if '/' in start_date:
                # Convert MM/DD/YYYY to YYYY-MM-DD
                parts = start_date.split('/')
                if len(parts[2]) == 4:  # YYYY format
                    start_date = f"{parts[2]}-{parts[0]:0>2}-{parts[1]:0>2}"
            
            end_date = dates[1] if len(dates) > 1 else start_date
            if '/' in end_date:
                parts = end_date.split('/')
                if len(parts[2]) == 4:
                    end_date = f"{parts[2]}-{parts[0]:0>2}-{parts[1]:0>2}"
            
            return start_date, end_date
        
        # Default to last 30 days for historical data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Check for relative time references
        if "last week" in query.lower():
            end_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        elif "last month" in query.lower():
            end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    
    def get_routes_data(self, origin: str, destination: str) -> List[Dict]:
        """
        Get route information between two airports using Amadeus.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            
        Returns:
            List of route data dictionaries
        """
        # Calculate a future date (30 days from now)
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"Using future date for flight search: {future_date}")
        
        endpoint = 'v2/shopping/flight-offers'
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': future_date,
            'adults': 1,
            'max': 5  # Reduced from 10 to 5 to avoid potential limits
        }
        
        response = self._make_amadeus_request(endpoint, params=params)
        
        if response and 'data' in response:
            return response['data']
        else:
            return []
    
    def get_historical_flights(self, origin: str, destination: str, 
                              start_date: str, end_date: str, limit: int = 100) -> List[Dict]:
        """
        Get flight data between two airports using Amadeus for multiple dates.
        
        Note: Amadeus doesn't provide true historical data, so we'll use flight offers search
        for future dates as a substitute for analysis purposes.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of results
            
        Returns:
            List of flight data
        """
        all_flights = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        # If dates are in the past, shift them to the future for Amadeus API
        today = datetime.now()
        if current_date < today:
            days_diff = (today - current_date).days + 1
            current_date = today + timedelta(days=1)
            end_date_obj = end_date_obj + timedelta(days=days_diff)
        
        # Make requests for different dates to gather flight data
        while current_date <= end_date_obj and len(all_flights) < limit:
            endpoint = 'v2/shopping/flight-offers'
            params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': current_date.strftime('%Y-%m-%d'),
                'adults': 1,
                'max': min(50, limit - len(all_flights))
            }
            
            response = self._make_amadeus_request(endpoint, params=params)
            
            if response and 'data' in response:
                # Add flight_date to each flight for compatibility with existing code
                for flight in response['data']:
                    flight['flight_date'] = current_date.strftime('%Y-%m-%d')
                all_flights.extend(response['data'])
            
            current_date += timedelta(days=1)
        
        return all_flights[:limit]
    
    def search_amadeus_flights(self, origin: str, destination: str, 
                              departure_date: str, return_date: str = None, 
                              adults: int = 1, max_results: int = 10) -> List[Dict]:
        """
        Search for flights using Amadeus Flight Offers Search API.
        
        Args:
            origin: Origin airport code (IATA)
            destination: Destination airport code (IATA)
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional for round-trip)
            adults: Number of adult passengers
            max_results: Maximum number of results to return
            
        Returns:
            List of flight offers with pricing information
        """
        # Ensure departure date is in the future (at least tomorrow)
        try:
            dep_date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
            today = datetime.now()
            
            # If departure date is not at least tomorrow, set it to tomorrow
            if dep_date_obj <= today:
                print(f"Warning: Departure date {departure_date} is not in the future. Using tomorrow's date instead.")
                departure_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
                
            # If return date exists and is not after departure date, set it to departure date + 7 days
            if return_date:
                ret_date_obj = datetime.strptime(return_date, '%Y-%m-%d')
                if ret_date_obj <= dep_date_obj:
                    print(f"Warning: Return date {return_date} is not after departure date. Using departure date + 7 days instead.")
                    return_date = (dep_date_obj + timedelta(days=7)).strftime('%Y-%m-%d')
        except ValueError:
            # If date parsing fails, use tomorrow for departure and departure + 7 for return
            print(f"Warning: Invalid date format. Using tomorrow's date for departure.")
            departure_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            if return_date:
                return_date = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        
        print(f"Searching flights: {origin} to {destination}, departure: {departure_date}, return: {return_date}, adults: {adults}")
        
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'max': min(max_results, 50)  # Reduced from 100 to 50 to avoid potential limits
        }
        
        if return_date:
            params['returnDate'] = return_date
        
        response = self._make_amadeus_request('v2/shopping/flight-offers', method='GET', params=params)
        
        if response and 'data' in response:
            return response['data']
        else:
            return []
    
    def get_cheapest_flights(self, origin: str, destination: str, 
                           departure_date: str = None, return_date: str = None, 
                           adults: int = 1, limit: int = 5) -> str:
        """
        Find cheapest flights between two airports using Amadeus API.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date in YYYY-MM-DD format (if None, uses tomorrow)
            return_date: Return date in YYYY-MM-DD format (optional for round-trip)
            adults: Number of adult passengers
            limit: Maximum number of results to return
            
        Returns:
            String with flight offers and pricing information
        """
        # Default to tomorrow if no departure date provided
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        flight_offers = self.search_amadeus_flights(
            origin, destination, departure_date, return_date, adults, limit * 2
        )
            
        if not flight_offers:
            return f"No flight offers found for {origin} to {destination} on {departure_date}."
            
        # Sort by price (total price for all passengers)
        sorted_offers = sorted(flight_offers, 
                             key=lambda x: float(x.get('price', {}).get('total', '999999')))
            
        trip_type = "round-trip" if return_date else "one-way"
        response = f"Cheapest {trip_type} flights from {origin} to {destination} on {departure_date}"
        if return_date:
            response += f" (returning {return_date})"
        response += f" for {adults} adult(s):\n\n"
            
        for i, offer in enumerate(sorted_offers[:limit], 1):
            price = offer.get('price', {})
            total_price = price.get('total', 'N/A')
            currency = price.get('currency', 'USD')
                
            # Extract itinerary information
            itineraries = offer.get('itineraries', [])
                
            response += f"{i}. ${total_price} {currency}\n"
                
            for j, itinerary in enumerate(itineraries):
                segments = itinerary.get('segments', [])
                duration = itinerary.get('duration', 'N/A')
                    
                direction = "Outbound" if j == 0 else "Return"
                response += f"   {direction}: {duration.replace('PT', '').replace('H', 'h ').replace('M', 'm')}\n"
                    
                for segment in segments:
                    departure = segment.get('departure', {})
                    arrival = segment.get('arrival', {})
                    carrier = segment.get('carrierCode', 'Unknown')
                    flight_num = segment.get('number', 'N/A')
                    aircraft = segment.get('aircraft', {}).get('code', 'N/A')
                        
                    dep_time = departure.get('at', '').split('T')
                    arr_time = arrival.get('at', '').split('T')
                        
                    dep_time_str = dep_time[1][:5] if len(dep_time) > 1 else 'N/A'
                    arr_time_str = arr_time[1][:5] if len(arr_time) > 1 else 'N/A'
                        
                    response += f"     {carrier}{flight_num}: {departure.get('iataCode', 'N/A')} {dep_time_str} → {arrival.get('iataCode', 'N/A')} {arr_time_str} ({aircraft})\n"
                
            # Show pricing breakdown if available
            price_breakdown = price.get('breakdown', [])
            if price_breakdown:
                response += f"   Price breakdown:\n"
                for breakdown in price_breakdown[:2]:  # Show first 2 items
                    passenger_type = breakdown.get('passengerType', 'Unknown')
                    quantity = breakdown.get('quantity', 1)
                    unit_price = breakdown.get('price', {}).get('total', 'N/A')
                    response += f"     {passenger_type} x{quantity}: ${unit_price} {currency}\n"
                
            response += "\n"
            
        # Add booking note
        response += f"💡 Prices are in {currency} and include taxes and fees.\n"
        response += f"⚠️  Prices may change. Book directly with the airline or through a travel agent to confirm availability and final pricing."
            
        return response
    
    def _get_amadeus_flight_analysis(self, origin: str, destination: str, 
                                      departure_date: str) -> str:
        """
        Method using Amadeus for route analysis.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            
        Returns:
            String with route analysis
        """
        # Get route information using Amadeus Flight Offers
        routes = self.get_routes_data(origin, destination)
        
        if not routes:
            print(origin, destination)
            return f"No route data found for {origin} to {destination}."
        
        # Analyze routes
        airlines = set()
        aircraft_types = set()
        
        for route in routes:
            # Extract airline information from Amadeus data structure
            for segment in route.get('itineraries', [])[0].get('segments', []):
                if segment.get('carrierCode'):
                    airlines.add(segment.get('carrierCode'))
                if segment.get('aircraft', {}).get('code'):
                    aircraft_types.add(segment.get('aircraft', {}).get('code'))
        
        response = f"Route analysis for flights from {origin} to {destination} on {departure_date}:\n\n"
        
        # Add airline information
        if airlines:
            response += "Airlines operating this route:\n"
            for airline in sorted(airlines):
                response += f"- {airline}\n"
        else:
            response += "No airline information available for this route.\n"
        
        # Add aircraft information
        if aircraft_types:
            response += "\nAircraft types used on this route:\n"
            for aircraft in sorted(aircraft_types):
                response += f"- {aircraft}\n"
        else:
            response += "\nNo aircraft information available for this route.\n"
        
        # Get flight data for analysis
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        start_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        flights = self.get_historical_flights(origin, destination, start_date, future_date, 100)
        
        # Add flight options information
        if flights:
            response += f"\nBased on {len(flights)} flight offers found:\n"
            
            # Analyze price ranges
            prices = []
            for flight in flights:
                if 'price' in flight:
                    try:
                        prices.append(float(flight['price']['total']))
                    except (ValueError, TypeError):
                        pass
            
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                response += f"Average price: ${avg_price:.2f}\n"
                response += f"Price range: ${min_price:.2f} - ${max_price:.2f}\n"
                
                # Calculate price variability
                if max_price > 0 and min_price > 0:
                    variability = (max_price - min_price) / min_price * 100
                    response += f"Price variability: {variability:.1f}%\n"
        else:
            response += "\nNo flight data available for price analysis.\n"
            
        best_day = day_names[sorted_days[0][0]]
        worst_day = day_names[sorted_days[-1][0]] if sorted_days[-1][1] > 0 else "N/A"
        
        response += f"\n{best_day} has the most flight options for this route.\n"
        if worst_day != "N/A":
            response += f"{worst_day} has the fewest flight options.\n"
        
        response += f"\nNote: This analysis is based on flight frequency, not pricing. "
        response += f"For actual fare comparison, check airline websites or booking platforms."
        
        return response
    
    def analyze_flight_data(self, query: str) -> str:
        """
        Analyze flight data based on the user's query.
        
        Args:
            query: User's query string
            
        Returns:
            String with analysis results
        """
        # Extract origin and destination from query
        origin, destination = self.extract_airports(query)
        
        if not origin or not destination:
            return ("I couldn't identify the origin and destination airports in your query. "
                   "Please specify them using airport codes (e.g., SFO, JFK) or full airport names.")
        
        # Extract date range from query
        departure_date, return_date = self.extract_date_range(query)
        
        # Check if it's a round-trip query
        is_round_trip = any(word in query.lower() for word in ['round trip', 'return', 'round-trip'])
        return_date_final = return_date if is_round_trip else None
        
        # Extract number of passengers
        adults = 1
        passenger_match = re.search(r'(\d+)\s*(?:adult|passenger|person)', query.lower())
        if passenger_match:
            adults = int(passenger_match.group(1))
        
        # Check if query is about cheapest day or day analysis
        if any(word in query.lower() for word in ['day', 'weekday', 'weekend', 'when', 'best day']):
            # Use Amadeus-based analysis instead of the old AviationStack-based one
            return self.get_cheapest_flights(origin, destination, departure_date, return_date_final, adults)
        
        # Default to cheapest flights search
        return self.get_cheapest_flights(origin, destination, departure_date, return_date_final, adults)
