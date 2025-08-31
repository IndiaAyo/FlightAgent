from typing import Annotated, Optional
from semantic_kernel.functions import kernel_function
from serpapi import GoogleSearch
import json
import os
from dotenv import load_dotenv


class FlightSearchPlugin:
    """A Semantic Kernel plugin for searching flights via SerpAPI.

    Methods are decorated with @kernel_function so the Semantic Kernel agent
    can discover and call them as tools.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SERP_API_KEY")

    @kernel_function(description="Search for flights using Google Flights via SerpAPI")
    def search_flights(
        self,
        departure: Annotated[str, "Departure airport code (e.g., LAX)"],
        type: Annotated[int, "one way or round trip. Round trip is 1, One way is 2"],
        arrival: Annotated[str, "Arrival airport code (e.g., JFK)"],
        outbound_date: Annotated[str, "Departure date (YYYY-MM-DD)"],
        return_date: Optional[Annotated[str, "Return date (YYYY-MM-DD) for round trips"]] = None,
    ) -> Annotated[str, "JSON string containing flight search results"]:
        """Search for flights using SerpAPI's Google Flights engine.

        This function calls the SerpAPI client and returns a JSON string
        with the raw response. The agent can parse and present results.
        """
        if not self.api_key:
            raise RuntimeError("SERP_API_KEY not set in environment")

        params = {
            "api_key": self.api_key,
            "engine": "google_flights",
            "departure_id": departure,
            "arrival_id": arrival,
            "outbound_date": outbound_date,
            "type": type,
            "hl": "en",
            "gl": "us",
            "currency": "USD",
        }

        if return_date:
            params["return_date"] = return_date

        # SerpAPI client is synchronous; call it directly (may block).
        search = GoogleSearch(params)
        results = search.get_dict()

        # Return JSON string
        return json.dumps(results)
