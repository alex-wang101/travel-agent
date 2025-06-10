from google.cloud import bigquery
import re

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
    
    def extract_airports(self, query):
        """Extract origin and destination airport codes from the query.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (origin, destination) airport codes, or (None, None) if not found
        """
        # First try to find direct airport codes (3 uppercase letters)
        airport_pattern = r'\b([A-Z]{3})\b'
        uppercase_query = query.upper()
        airports = re.findall(airport_pattern, uppercase_query)
        
        if len(airports) >= 2:
            return airports[0], airports[1]
        
        # Look for common patterns in flight queries with airport codes
        from_pattern = r'from\s+([A-Z]{3})'
        to_pattern = r'to\s+([A-Z]{3})'
        
        from_match = re.search(from_pattern, uppercase_query)
        to_match = re.search(to_pattern, uppercase_query)
        
        if from_match and to_match:
            return from_match.group(1), to_match.group(1)
        
        # If we can't find airport codes, try to find airport names
        words = uppercase_query.split()
        
        # Try to find airport names in the query
        origin = None
        destination = None
        
        # Look for airport names after 'from' and 'to'
        if 'FROM' in words:
            from_index = words.index('FROM')
            # Check for airport names in the next few words
            for i in range(1, min(4, len(words) - from_index)):
                potential_name = ' '.join(words[from_index + 1:from_index + i + 1])
                if potential_name in self.airport_mapping:
                    origin = self.airport_mapping[potential_name]
                    break
        
        if 'TO' in words:
            to_index = words.index('TO')
            # Check for airport names in the next few words
            for i in range(1, min(4, len(words) - to_index)):
                potential_name = ' '.join(words[to_index + 1:to_index + i + 1])
                if potential_name in self.airport_mapping:
                    destination = self.airport_mapping[potential_name]
                    break
        
        # If we still don't have both origin and destination, try scanning for any airport name
        if not origin or not destination:
            # Try combinations of 1-3 consecutive words
            for i in range(len(words)):
                for j in range(1, 4):
                    if i + j <= len(words):
                        potential_name = ' '.join(words[i:i+j])
                        if potential_name in self.airport_mapping:
                            # If we haven't found origin yet, this is origin
                            if not origin:
                                origin = self.airport_mapping[potential_name]
                            # Otherwise, if we haven't found destination, this is destination
                            elif not destination:
                                destination = self.airport_mapping[potential_name]
                            # If we have both, we can stop
                            if origin and destination:
                                break
        
        return origin, destination
    
    def extract_year(self, query):
        """Extract year from the query if present.
        
        Args:
            query: User's query string
            
        Returns:
            Year as integer or None if not found
        """
        # Look for year patterns like "2022" or "in 2022"
        year_pattern = r'\b(20\d{2})\b'
        match = re.search(year_pattern, query)
        
        if match:
            return int(match.group(1))
        
        # Check for relative time references
        if "last year" in query.lower():
            return 2022  # Using 2022 as "last year" for this example
        
        # Default to 2022 if no year specified
        return 2022
    
    def get_cheapest_flights(self, origin, destination, year=2022, limit=5):
        """Query BigQuery for the cheapest flights between two airports.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            year: Year to filter results
            limit: Maximum number of results to return
            
        Returns:
            DataFrame with the cheapest flights
        """
        if not self.client:
            return "BigQuery client not initialized. Please authenticate first."
        
        query = f"""
        SELECT
            carrier,
            flight_number,
            origin_airport_code,
            destination_airport_code,
            total_fare,
            departure_date
        FROM
            `bigquery-public-data.flights.flights`
        WHERE
            origin_airport_code = '{origin}' 
            AND destination_airport_code = '{destination}'
            AND year = {year} 
            AND total_fare IS NOT NULL
        ORDER BY
            total_fare ASC
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
            cheapest_fare = df['total_fare'].min()
            avg_fare = df['total_fare'].mean()
            carriers = df['carrier'].unique()
            
            response = f"Based on historical data for flights from {origin} to {destination} in {year}:\n"
            response += f"The cheapest fare found was ${cheapest_fare:.2f}.\n"
            response += f"The average fare was ${avg_fare:.2f}.\n"
            response += f"The main carriers were: {', '.join(carriers)}.\n\n"
            
            response += "Top 5 cheapest flights:\n"
            for i, row in df.iterrows():
                response += f"{i+1}. ${row['total_fare']:.2f} - {row['carrier']} {row['flight_number']} on {row['departure_date']}\n"
            
            return response
            
        except Exception as e:
            return f"Error querying BigQuery: {str(e)}"
    
    def get_cheapest_day(self, origin, destination, year=2022):
        """Find which day of the week is cheapest to fly between two airports.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            year: Year to filter results
            
        Returns:
            String with analysis of cheapest day to fly
        """
        if not self.client:
            return "BigQuery client not initialized. Please authenticate first."
        
        query = f"""
        SELECT
            EXTRACT(DAYOFWEEK FROM departure_date) as day_of_week,
            AVG(total_fare) as avg_fare,
            COUNT(*) as num_flights
        FROM
            `bigquery-public-data.flights.flights`
        WHERE
            origin_airport_code = '{origin}' 
            AND destination_airport_code = '{destination}'
            AND year = {year} 
            AND total_fare IS NOT NULL
        GROUP BY
            day_of_week
        ORDER BY
            avg_fare ASC
        """
        
        try:
            # Run the query
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert to DataFrame
            df = results.to_dataframe()
            
            if df.empty:
                return f"No flight data found for {origin} to {destination} in {year}."
            
            # Map day numbers to names (1=Sunday, 2=Monday, etc.)
            day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                        5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
            
            df['day_name'] = df['day_of_week'].map(day_names)
            
            # Format the response
            cheapest_day = df.iloc[0]
            most_expensive_day = df.iloc[-1]
            
            response = f"Analysis of flight prices from {origin} to {destination} in {year} by day of week:\n\n"
            response += f"The cheapest day to fly is {cheapest_day['day_name']} with an average fare of ${cheapest_day['avg_fare']:.2f}.\n"
            response += f"The most expensive day to fly is {most_expensive_day['day_name']} with an average fare of ${most_expensive_day['avg_fare']:.2f}.\n\n"
            
            response += "Average fares by day of week (from cheapest to most expensive):\n"
            for i, row in df.iterrows():
                response += f"{row['day_name']}: ${row['avg_fare']:.2f} (based on {int(row['num_flights'])} flights)\n"
            
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
        
        # Extract year from query
        year = self.extract_year(query)
        
        # Check if query is about cheapest day
        if any(word in query.lower() for word in ['day', 'weekday', 'weekend', 'when']):
            return self.get_cheapest_day(origin, destination, year)
        
        # Default to cheapest flights
        return self.get_cheapest_flights(origin, destination, year)