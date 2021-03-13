CS50: Final project
CS50 News Aggregator
Jordan Lafrenière
Nagoya, Japan

About:
- A Basic news aggregator which separates the news based on "left wing" to "right wing" bias.
    -> This example is using the newsAPI.com API to ”scrape” the news items.
    -> News political leaning (Left ←→ Right) is dependent on the source (CNN, FOX..etc.). For this example, the Leaning of the sources is taken from allsides.com.
- The purpose is to combat misinformation and allow users to interact.
    -> Users can like and comment on articles.
    -> Articles are ordered by popularity (number of likes).

User Roles:
There are 3 main classes of users:
- Guests
- Regular user
- Administrator

User Roles - Guests
Guests can :
   -> view the news
   -> view the comments
   -> view the number of likes
   -> register

User Roles – Regular User
Regular users can:
   -> view the news
   -> post and view comments
   -> like and view the number of likes
   -> edit own user profile

User Roles - Administrator
  -> Administrators can:
  -> view the news, post and view comments, like and view the number of likes
  -> edit profile for all users, including the ability
     - to set the user as administrator and,
     - to delete users
  -> edit/add/delete news sources (change the name, URL, leaning).
     - Can also disable a source so that it no longer shows up on the index (but articles are still in database and will re-appear if source is “re-abled”)
  -> update the news shown on the index by fetching the latest data from newsAPI

Issues and Possible Improvements
- News scrapping should be automated (daily or hourly), at the moment, an administrator user needs to manually "fetch the news"
- Currently, the only visible news is a "top ten" from latest ”scrape”. Ideally, the index  page would be "multi-page" so that the user can view the news from previous days.
- Content of the news article is not fully visible in free newsAPI version.
- Website should use Flask "role" feature for role access control. Currently, website is using a simple if statement to check if the user is admin. This is dangerous since, for example, somebody could easily guess the name of the "is_admin" variable in the MYSQL DB and generate a query to register themselves as admin.
- Many other features that are common to social medias which would eventually need to be added (sorting, blocking, private messaging, sharing, profiles, following...etc.)
- Layout is not the most user friendly, and design is not the most efficient.
