from datetime import datetime
from typing import Literal
import pytz

from langchain.tools import tool
from src.service.GoogleService import GoogleService
from src.service.WeatherService import WeatherService  # 从weather分支添加的天气服务
from src.config import settings


# Lazy import for Tavily to avoid import errors if not configured
_tavily_client = None

def _get_tavily_client():
    """Lazy initialization of Tavily client"""
    global _tavily_client
    if _tavily_client is None and settings.tavily_api_key:
        from tavily import TavilyClient
        _tavily_client = TavilyClient(api_key=settings.tavily_api_key)
    return _tavily_client


googleService = GoogleService()
weatherService = WeatherService()

# Import Google Maps tools (Direct API)
try:
    from src.tools.GoogleMapTools import get_google_maps_tools
    GOOGLE_MAPS_AVAILABLE = True
except ImportError:
    GOOGLE_MAPS_AVAILABLE = False
    get_google_maps_tools = lambda: []
    print("Warning: Google Maps tools not available")

@tool
def sendEmail(to_list: str, subject: str, message_text: str):
    """
    Sends an email to the specified recipient.

    Parameters:
    ----------
    to : str
        The recipient's email address (e.g., "someone@example.com" as a list
    subject : str
        The subject line of the email.
    message_text : str
        The full body of the email.

    Returns:
    -------
    str
        A confirmation message indicating that the email was sent successfully,
        or an error message if it failed.

    Notes:
    -----
    - Ensure 'to' is a valid email address.
    - This tool cannot guess the recipient or subject; they must be provided.
    - Use this tool only for sending plain-text emails.
    """
    if len(to_list) == 1:
        to = to_list[0]
    else:
        to = to_list.join(" ,")
    print("Sending email...")
    googleService.sendEmail(to, subject, message_text)
    return "Sent an email to {}".format(to)

@tool
def createBookingEvent(summary : str, description : str, start_time : datetime, end_time : datetime, attendees_emails_list=None):
    """
        Creates a Google Calendar event.

        Parameters:
        ----------
            summary : Summary of the event
            description : Description of the event
            start_time : Start time of the event
            end_time : End time of the event
            attendees_emails_list : List of attendee emails
    """
    print("About to create booking event")
    return googleService.createBookingEvent(summary, description, start_time, end_time, attendees_emails_list)

@tool
def readCalendarEvents(start_time: datetime, end_time: datetime, max_results: int = 10) -> str:
    """
    Read calendar events within a specified time range.
    
    Parameters:
    ----------
    start_time : datetime
        Start of the time range to query events
    end_time : datetime
        End of the time range to query events
    max_results : int, optional
        Maximum number of events to return (default: 10)
    
    Returns:
    -------
    str
        Formatted list of calendar events with details including:
        - Event title (summary)
        - Start and end time
        - Description
        - Location
        - Attendees
        - Event link
    
    Notes:
    -----
    - Use this tool to check upcoming events, view schedule, or find specific meetings
    - Events are returned in chronological order
    - Use getCurrentTime() first to get the current date/time for relative queries
    - For "today's events", set start_time to today 00:00 and end_time to today 23:59
    - For "this week's events", calculate the week range accordingly
    """
    print("Reading calendar events...")
    events = googleService.getCalendarEvents(start_time, end_time, max_results)
    
    if not events:
        return f"No events found between {start_time.strftime('%Y-%m-%d %H:%M')} and {end_time.strftime('%Y-%m-%d %H:%M')}"
    
    # Format events for display
    formatted_output = []
    formatted_output.append(f"Found {len(events)} event(s):\n")
    
    for idx, event in enumerate(events, 1):
        formatted_output.append(f"{idx}. {event['summary']}")
        formatted_output.append(f"   Time: {event['start']} to {event['end']}")
        
        if event['description']:
            formatted_output.append(f"   Description: {event['description']}")
        
        if event['location']:
            formatted_output.append(f"   Location: {event['location']}")
        
        if event['attendees']:
            formatted_output.append(f"   Attendees: {', '.join(event['attendees'])}")
        
        formatted_output.append(f"   Link: {event['htmlLink']}")
        formatted_output.append("")  # Empty line between events
    
    return "\n".join(formatted_output)

@tool
def searchEmail(query : str):
    """
        Search emails using gmail api.
        Parameters:
            query : valid email search query that can be used in google api
        :return
            messages
    """
    print("Searching emails...")
    return googleService.searchEmail(query)

@tool
def createDriveDocument(documentName : str, documentContent : str):
    """
    Creates a Google Drive document.
    Parameters:
    :param documentName:
    :param documentContent:
    :return: document link
    """
    print("About to create drive document")
    return googleService.createDocumentInDrive(documentName, documentContent)

@tool
<<<<<<< HEAD
def getCurrentTime() -> str:
    """
    Get the current date and time with timezone information.
    
    Returns:
    -------
    str
        Current date, time, day of week, week number, and timezone information
    
    Notes:
    -----
    - Use this tool when you need to know the current time for scheduling, 
      time-based queries, or date calculations
    - Returns time in the configured timezone (from GOOGLE_CALENDAR_TIMEZONE)
    - Includes day of week and ISO week number for better context
    """
    # Get timezone from settings
    tz = pytz.timezone(settings.google_calendar_timezone)
    now = datetime.now(tz)
    
    # Format comprehensive time information
    day_of_week = now.strftime("%A")  # Full day name (e.g., "Monday")
    week_number = now.isocalendar()[1]  # ISO week number
    
    return (
        f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Day: {day_of_week}\n"
        f"Week: {week_number}\n"
        f"Timezone: {settings.google_calendar_timezone}"
    )

@tool
def webSearch(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news"] = "general",
    include_raw_content: bool = False
) -> str:
    """
    Search the web for information using Tavily search API.
    
    Parameters:
    ----------
    query : str
        The search query string
    max_results : int, optional
        Maximum number of search results to return (default: 5)
    topic : Literal["general", "news"], optional
        Type of search - "general" for web search or "news" for news articles (default: "general")
    include_raw_content : bool, optional
        Whether to include full page content in results (default: False)
=======
def getWeather(location: str, date: str = None):
    """
    Queries weather information for a specific location and date.
    
    Parameters:
    ----------
    location : str
        The city or location name (e.g., "Beijing", "New York", "Shanghai")
    date : str, optional
        The date to query weather for in format "YYYY-MM-DD".
        If not provided, returns current weather.
>>>>>>> feature/weather-check
    
    Returns:
    -------
    str
<<<<<<< HEAD
        Search results with titles, URLs, and snippets
    
    Notes:
    -----
    - Use this tool to find current information, news, or facts from the internet
    - Requires TAVILY_API_KEY to be configured in settings
    - Returns formatted search results with relevant information
    """
    tavily_client = _get_tavily_client()
    
    if not tavily_client:
        return "Error: Web search is not available. TAVILY_API_KEY is not configured."
    
    try:
        results = tavily_client.search(
            query=query,
            max_results=max_results,
            topic=topic,
            include_raw_content=include_raw_content
        )
        
        # Format the results for better readability
        formatted_results = []
        for idx, result in enumerate(results.get('results', []), 1):
            formatted_results.append(
                f"{idx}. {result.get('title', 'No title')}\n"
                f"   URL: {result.get('url', 'No URL')}\n"
                f"   {result.get('content', 'No content')}\n"
            )
        
        return "\n".join(formatted_results) if formatted_results else "No results found."
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"
=======
        Weather information including temperature, conditions, humidity, etc.
    
    Notes:
    -----
    - Supports major cities worldwide
    - Date parameter is optional; defaults to current weather
    - Returns forecast data if date is in the future
    """
    print(f"Querying weather for {location}...")
    return weatherService.get_weather(location, date)
>>>>>>> feature/weather-check
