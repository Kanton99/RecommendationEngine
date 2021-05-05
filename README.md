# Recommendation Engine

## Usage
Create an envirnoment, and start test_rest.py. Once it booted up to get a recommendation for a user, do a get call with this format
```
 curl -X GET http://localhost:5000/recommend -d "userID=*user id*" 
 
```
and the system will return the top ten recommendation for that user.
By passing also ```-d "assetId=*asset id*"``` the system will also diplay recommendations related to that asset and add that asset to the list tha assets that the user has interacted with.

The data files supplied to the system must be .json files, and there must be two kinds:
 1 Interaction files, where are written user-asset interactions, with at least user id and asset id per interaction
 2 Asset files, where is stored the asset data data, with at least the asset id

### Config File
 - The config file can be changed to fit whatever json files you use.
 - "data directory location" is where are your file stored.
 - "user interaction file pattern" and "asset data file pattern" are the pattern to search in the file names to recognize what files to look for.
 - "asset ID key" and "user ID key" are the key to find the user IDs and asset IDs.
 - "asset tags" the features that an asset is defined by.
 









 
