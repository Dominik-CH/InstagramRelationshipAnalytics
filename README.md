# InstagramRelationshipAnalytics

## General Info
This Tool helps scrape follower/followings from any public instagram user and displays their connection to each other.
<br>
I am using my own fork of the <a href="https://github.com/Dominik-CH/instagram-scraper">instagram-scraper library</a> to get:<br>
Main User | Dependent 
---------|----------
Follower | Following 
Follower | Follower
Following | Following
Following | Follower 

You are able to set how many followers/following you want to scrape from each individual account.<br>
These users and their followers/followings are stored in an SQLite Database.<br>
<br>The graph is then processed with the help of networkx and displayed using matplotlib.<br>
You can also specify a threshold that each user in the database has to have at least a certain amount of edges to be part of the graph, to filter out irrelevant accounts.<br>
Pictures are being downloaded and saved - to make the graph look more appealing for the enduser - only if the threshold is met.


## Example Graph using <a href="instagram.com/der_ziz">Der_Ziz</a>

Exported Graph:<br>
<img src="media/DerZizInGrossDownscaled.png"  alt="Der_Ziz Graph"/><br>
<br><br>
<img src="media/DerZizAusschnitt.png"  alt="Der_Ziz Ausschnitt"/><br>



## Relationship Analytics Tool in action

<img src="media/ToolGIF.gif"  alt="Relationship Analytics in Action"/>


