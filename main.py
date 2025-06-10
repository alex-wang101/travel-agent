import os
import sys
from dotenv import load_dotenv
from agents.route_agent import InquiryRouterAgent
from agents.flight_status_agent import FlightStatusAgent
from agents.flight_analytics_agent import FlightAnalyticsAgent
import colorama
from colorama import Fore, Style

def print_welcome():
    """Print a welcome message for the Smart Travel Assistant."""
    print(Fore.CYAN + "\n" + "="*60)
    print(" "*15 + "SMART TRAVEL ASSISTANT")
    print("="*60 + Style.RESET_ALL)
    print(Fore.YELLOW + "\nWelcome to your Smart Travel Assistant!")
    print("You can ask about:")
    print("  1. Flight status (e.g., 'What is the status of flight AA123?')")
    print("  2. Flight price analysis (e.g., 'What were the cheapest flights from JFK to LAX last year?')")
    print(Fore.GREEN + "\nType 'exit' to quit the assistant." + Style.RESET_ALL)
    print("\n")

def main():
    """Main function to run the Smart Travel Assistant."""
    # Initialize colorama for cross-platform colored terminal output
    colorama.init()
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys from environment variables
    aviation_api_key = os.getenv("AVIATIONSTACK_API_KEY")
    
    # Check if API key exists
    if not aviation_api_key:
        print(Fore.RED + "Error: AVIATIONSTACK_API_KEY not found in .env file" + Style.RESET_ALL)
        print("Please create a .env file with your AviationStack API key.")
        sys.exit(1)
    
    # Initialize agents
    try:
        flight_status_agent = FlightStatusAgent(aviation_api_key)
        flight_analytics_agent = FlightAnalyticsAgent()
        router_agent = InquiryRouterAgent(flight_status_agent, flight_analytics_agent)
        
        print_welcome()
        
        # Main interaction loop
        while True:
            # Get user input
            user_query = input(Fore.CYAN + "\nHow can I help you? " + Style.RESET_ALL)
            
            # Check for exit command
            if user_query.lower() in ['exit', 'quit', 'bye']:
                print(Fore.YELLOW + "\nThank you for using Smart Travel Assistant. Goodbye!" + Style.RESET_ALL)
                break
            
            # Process the query through the router agent
            if user_query.strip():
                print(Fore.MAGENTA + "\nProcessing your request..." + Style.RESET_ALL)
                response = router_agent.route_query(user_query)
                print(Fore.GREEN + "\nResult:" + Style.RESET_ALL)
                print(response)
            else:
                print(Fore.RED + "Please enter a valid query." + Style.RESET_ALL)
                
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {str(e)}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
