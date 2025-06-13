import re
from datetime import datetime, timedelta
from google.cloud import bigquery

class FlightAnalyticsAgent:
    """Agent responsible for analyzing historical flight data.
    
    This agent queries Google BigQuery's public flight dataset to answer
    analytical questions about flights, prices, and trends.
    """
    
    def __init__(self):
        """Initialize the FlightAnalyticsAgent with a BigQuery client."""
        try:
            self.client = bigquery.Client()
            print("BigQuery client initialized successfully")
        except Exception as e:
            print(f"Error initializing BigQuery client: {str(e)}")
            print("Make sure you have authenticated with 'gcloud auth application-default login'")
            self.client = None
            
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
    
    def extract_airports(self, query: str) -> tuple[str, str]:
        """
        Extract origin and destination airport codes from the query.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (origin, destination) airport codes
        """
        # Convert query to uppercase for matching airport codes
        query_upper = query.upper()
        
        # List to store found airport codes
        found_airports = []
        
        # First check for exact IATA codes in the query
        for code in re.findall(r'\b([A-Z]{3})\b', query_upper):
            # Skip common three-letter words
            if code not in {'THE', 'AND', 'FOR', 'ARE', 'NOT', 'BUT', 'ONE', 'TWO', 'WHO', 'HOW', 'WHY'}:
                found_airports.append(code)
                if len(found_airports) >= 2:
                    break
        
        # If we don't have 2 airports yet, check for airport names in our mapping
        if len(found_airports) < 2:
            query_lower = query.lower()
            
            # Check both keys and values in the airport_mapping
            for airport_name, code in self.airport_mapping.items():
                if airport_name.lower() in query_lower and code not in found_airports:
                    found_airports.append(code)
                    if len(found_airports) >= 2:
                        break
        
        # If we found at least one airport
        if found_airports:
            # If we found only one, use it as origin and default destination
            if len(found_airports) == 1:
                return found_airports[0], "LAX"
            # If we found two or more, use the first two
            else:
                return found_airports[0], found_airports[1]
        
        return "Could not find airports", "in query"

    def extract_date_range(self, query: str) -> tuple[str, str]:
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
        
        # Default to 2022 for historical data (assuming that's the year in your dataset)
        default_year = 2013
        
        # Check for specific year mentions
        year_pattern = r'\b(20\d{2})\b'
        year_match = re.search(year_pattern, query)
        if year_match:
            default_year = int(year_match.group(1))
        elif "last year" in query.lower():
            default_year = 2013  # Assuming 2022 is "last year" for this dataset
        
        # Create dates with the identified year
        end_date = f"{default_year}-12-31"
        start_date = f"{default_year}-01-01"
        
        # Check for relative time references within the year
        if "last month" in query.lower():
            end_date = f"{default_year}-12-31"
            start_date = f"{default_year}-12-01"
        elif "last week" in query.lower():
            end_date = f"{default_year}-12-31"
            start_date = f"{default_year}-12-24"
        
        return start_date, end_date

    def get_flights_info(self, origin, destination, date_range=None, limit=5):
        """Query BigQuery for flight information between two airports.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            year: Year to filter results
            limit: Maximum number of results to return
            
        Returns:
            DataFrame with flight information
        """
        if not self.client:
            return "BigQuery client not initialized. Please authenticate first."
        
        # If date_range is provided, use it; otherwise default to 2022
        year = 2013  # Default year if no date range is provided
        
        if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
            # Extract year from the start date in the tuple
            try:
                # Try to extract year from YYYY-MM-DD format
                year = int(date_range[0].split('-')[0])
            except (IndexError, ValueError, AttributeError):
                # If extraction fails, keep the default year
                pass
        
        query = f"""
        SELECT
            carrier,
            origin,
            dest,
            hour,
            dep_delay
        FROM
           `bright-velocity-457221-i0.flight_data.cheapest_prices`
        WHERE
            origin = '{origin}' 
            AND dest = '{destination}'
            AND year = {year}
        ORDER BY
            dep_delay ASC
        LIMIT {limit}
        """
        
        try:
            # Run the query
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert to DataFrame
            df = results.to_dataframe()
            
            if df.empty:
                return f"No flight data found for {origin} to {destination} in {year}."
            
            # Format the response
            carriers = df['carrier'].unique()
            avg_delay = df['dep_delay'].mean()
            
            response = f"Based on historical data for flights from {origin} to {destination} in {year}:\n"
            response += f"The main carriers were: {', '.join(carriers)}.\n"
            response += f"Average departure delay: {avg_delay:.1f} minutes.\n\n"
            
            # Add details for each flight
            response += "Flight details:\n"
            for _, row in df.iterrows():
                delay = row['dep_delay']
                if delay > 0:
                    delay_text = f"Delayed by {delay:.0f} min"
                elif delay < 0:
                    delay_text = f"Departed {abs(delay):.0f} min early"
                else:
                    delay_text = "On time"

                response += f"- {row['carrier']}: {row['origin']} to {row['dest']} at {row['hour']}:00, Status: {delay_text}\n"
                response += "penar"
            
            return response 
            
        except Exception as e:
            return f"Error querying BigQuery: {str(e)}"

    
    def get_best_on_time_carriers(self, origin, destination, date_range=None):
        """Find carriers with the best on-time performance between two airports.
        
        For each carrier, retrieves the 10 flights with the least delay time and calculates
        the average delay time per carrier.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            date_range: Tuple of (start_date, end_date) or None
            
        Returns:
            String with analysis of carriers ranked by on-time performance
        """
        if not self.client:
            return "BigQuery client not initialized. Please authenticate first."
        
        try:
            # Query to get the 10 flights with least delay for each carrier
            query = f"""
            WITH RankedFlights AS (
                SELECT
                    carrier,
                    arr_delay,
                    ROW_NUMBER() OVER (PARTITION BY carrier ORDER BY arr_delay ASC) as rank
                FROM
                    `bright-velocity-457221-i0.flight_data.cheapest_prices`
                WHERE
                    origin = '{origin}' 
                    AND dest = '{destination}'
                    AND arr_delay IS NOT NULL
            )
            SELECT
                carrier,
                AVG(arr_delay) as average_arrival_delay,
                COUNT(*) as flight_count
            FROM
                RankedFlights
            GROUP BY
                carrier
            ORDER BY
                ABS(average_arrival_delay) ASC
            """
            
            # Run the query
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert to DataFrame
            df = results.to_dataframe()
            
            if df.empty:
                return f"No flight data found for {origin} to {destination}."
            
            # Format the response
            response = f"Based on historical data for flights from {origin} to {destination}, the airlines with the best on-time performance were:\n\n"
            
            for i, (_, row) in enumerate(df.iterrows(), 1):
                response += f"#{i}. {row['carrier']} (avg delay: {row['average_arrival_delay']:.1f} min, based on {int(row['flight_count'])} flights)\n"
            
            return response
            
        except Exception as e:
            return f"Error querying BigQuery: {str(e)}"
    
    def analyze_flight_data(self, query):
        """Analyze flight data based on the user's query.
        
        Args:
            query: User's query string
            
        Returns:
            String with analysis results
        """
        # Extract origin and destination from query
        origin, destination = self.extract_airports(query)
        
        if not origin or not destination:
            return "I couldn't identify the origin and destination airports in your query. Please specify them using airport codes (e.g., SFO, JFK)."
        
        # Extract date range from query
        date_range = self.extract_date_range(query)
        
        # Check if query is about on-time performance or carriers
        return self.get_best_on_time_carriers(origin, destination, date_range)