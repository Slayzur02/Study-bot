# Testing bot with Selenium - Python
A small python project that automates the majority of the online testing process at Vietnam during the Covid-19 outbreak. While heavy use of the project is possible for all tests, this is not advised as certain tests are still worth doing to solidify your knowledge.  
  
It is to note, that this is very useful for the completion certain tests that will not be assessed during the future graduation tests, as well as preparation and learning.  
  
## Technology   
Selenium (Python), Geckodriver for firefox, and a few small packages that aid the process of development and usability.  
  
## Implementation
The bot uses a "irrelevant" account to mark down all questions and the associated answers, as well as their associated IDs to replicate the server-side database.   
  
It then uses trial-and-error to randomly mark answers, then hits the json-api (exposed by the front-end code) to mark every answer as "correct" or "wrong". Since the multiple choice only comes with 4 choices, it essentially takes 4 tries for the bot to get a full score.  
  
Since the site is also faulty (it sometimes mixes the IDs), I have added 2 tests and fixes on the stored/ replicated databases of question and answers to ensure its accuracy. This can cover most (but not all) of the cases.  
  
With this set of data, the bot can either leave the user to fill out the test with its answers, or fill it in itself (while replicating human-like behavior).
  
## Improvements
There are 2 quick possible improvements to the bot.
* Building a full-on website to aid the automation of many accounts:
While the bot does its job fairly well, it lacks the ability to check for multiple accounts at the same time. A full-on server with perhaps a small subscription fee could help automate even more tasks, and introduce it to students that aren't too familiar with code
* Adding extra threads to check changes and fixes in the application: This is crucial as small changes (for example, in classes or structuring of the front end, as well as encryption of the question/ answerIDs) may completely cripple the bot. While this can be fixed easily if known, even small delays in fixing can cause numerous problems for the users.