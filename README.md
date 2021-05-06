# Recommendation Engine

## Requirements
This API requires to be installed on a Linux distribution and to have Python3.6+ installed

## Installation
 1. Clone the repository with ```git clone https://github.com/Kanton99/RecommendationEngine.git``` 
 2. Create a Python virtual environment with ```python3 -m venv *environment name*``` 
 3. Activate the envirnment with ```source *repository path*/*environment name*/bin/activate``` 
 4. Install the required libraries with ```python3 -m pip install -r requirements.txt``` 

## Usage
To use the API start RecommendServer.py. Once it booted up to get a recommendation for a user, do a get call with this format

```curl -X GET http://localhost:5000/recommend -d "userID=*user id*"```

and the system will return the top ten recommendation for that user.
By passing also ```-d "assetId=*asset id*"``` the system will also diplay recommendations related to that asset and add that asset to the list tha assets that the user has interacted with.

### Movielens
By setting in config.json 'use_movielens' to true the system will use the movielens dataset.

### Data files
The data files supplied to the system must be .json files, and there must be two kinds:
 1. Interaction files, where are written user-asset interactions, with at least user id and asset id per interaction
 2. Asset files, where is stored the asset data data, with at least the asset id
#### Example
interaction file name: interactions_#####.json
interaction file format: {"user_id":"#######","asset_id":"##########"}

video file name: video_#######.json
video file format:{"asset_id":"###########","tags":["t1","t2","t3"]}

user file name: user_#######.json
user file format: {"user_id":"#########","tags":["t1","t2","t3"]}

### Config File
 The config file can be changed to fit whatever json files you use.
 - "use_movielens" to tell the system to use the movielens dataset instead of your data files.
 - "data_directory_location" is where are your file stored.
 - "item_data_file_pattern" is the pattern to search in the file names to find item data.
 - "user_data_file_pattern" is the pattern to search in the file names to find user data.
 - "user_interaction_file_pattern" is the pattern to search in the file names to find interaction data.
 -  
 - "item_ID_key" and "user_ID_key" are the key to find the user IDs and asset IDs.
 - "item_tags" key in the item jsons to find the item features.
 - "user_tags" key in the user jsons to find the user features.
 









 
