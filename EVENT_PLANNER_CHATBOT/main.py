import sys
from agent import TravelAgent
from colorama import Fore, Style, init

# Initialize colors
init(autoreset=True)

def main():
    print(Fore.CYAN + "\n🌍 AI Travel Planner Initialized...")
    print(Fore.CYAN + "Try: 'Plan a day in Paris for tomorrow. I love jazz, history, and quiet places.'\n")

    agent = TravelAgent()

    while True:
        user_input = input(Fore.YELLOW + "You: " + Style.RESET_ALL)
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            print(Fore.WHITE + "Thinking... (Fetching APIs & Ranking)")
            
            itinerary = agent.generate_itinerary(user_input)
            
            print(Fore.GREEN + "\n🗓️  HERE IS YOUR PERFECT ITINERARY:\n")
            for item in itinerary:
                print(f"{Fore.MAGENTA}{item['time_slot']}{Style.RESET_ALL} - {Style.BRIGHT}{item['activity']}{Style.RESET_ALL}")
                print(f"   📍 {item['location']}")
                print(f"   💡 {item['notes']}")
                print("-" * 40)
            
        except Exception as e:
            print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main()