# skill-assessment
This is a command-line Python program that takes the name of a musical artist as input, and uses the [Genius API](https://docs.genius.com/) to output a list of that artist's songs. Note that songs that an artist was featured in will not appear.

## Installation
This program requires [Python 3.8](https://www.python.org/downloads/release/python-380/). Required packages can be found in `requirements.txt`. These can be installed via  
>$ pip install -r requirements.txt

## Running skill-assessment
A Genius API key is required to run skills-assessment, which can be acquired by making an account and creating an API Client [here](https://genius.com/api-clients). Generate a client access token, and save it in a file called `.env` with the following format:  
>ACCESS_TOKEN=#your access token here
  
To run skill-assessment, run  
>$ python get_songs.py  

At the prompt, enter the name of a musical artist and hit enter.  
  
## Testing
Unit tests are provided. Run with
>$ python test.py



