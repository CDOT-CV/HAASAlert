## Project Description

This project is an open source, proof of concept for hosting HAAS Alert data in the real time data hub hosted by CDOT. The purpose of this tool is to read off of the HAAS Alert websocket and post the recieved messages to a realtime data hub to get more information about the current status of traffic, incidents, and vehicle locations primarily in the Denver Metro area. 

## Prerequisites

Requires:

- Python 3.6 (or higher)
  - xmltodict
  - jsonschema
  - shapely
   
  
## Environment Setup

This code requires Python 3.6 or a higher version. If you haven’t already, download Python and Pip. Next, you’ll need to install several packages that we’ll use throughout this tutorial. You can do this by opening terminal or command prompt on your operating system:

```
pip install -r requirements.txt
```