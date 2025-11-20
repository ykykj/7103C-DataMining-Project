from datetime import datetime
from typing import Literal
import pytz

from langchain.tools import tool
from src.service.GoogleService import GoogleService
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
    
    Returns:
    -------
    str
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