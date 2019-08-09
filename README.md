# Personalized-Hiking-Suggestions
(An intelligent recommendation engine for finding similar hikes)

# Introduction

  AllTrails has the largest collection of trail guides. It has 75k+ trails information and more
than 10 million active users. It gives users the ability to search for hikes via custom filtering of
specific hiking trail attributes like distance, elevation gain and difficulty. But it doesn’t have the
intelligent recommendation engine based on the past experience.

  In this project, I have built a web application that provides personalized hiking
suggestions in California based on the past experience i.e if I liked hike X, I’ll like to hike Y
because it has similar hiking trail features.

# Data collection

  Scraping data was a challenging task. I did it in two phases. First I scraped the list of best
trails in California from a hiking website. Then using this list I scraped the hike metadata like
difficulty level, trail length, elevation gain, rating, route type and trail traffic information of each
trail. I used selenium package for scraping. Since this is my first project that involved web
scraping the scraped data ended up being messy. I had to do a lot of preprocessing to clean the
data before building recommendation engine. For the analysis, I used most of the hike attributes
as features.

# Methodology

  I used content based filtering for this recommendation system. I followed the below steps
● Start with a hike we know user likes
● Calculate similarity between this hike and all other hikes
● Recommend the ones that are most similar to the hike we started with
● I have also solved the cold start problem by recommending the most popular hikes

# Web application:
  https://personalizedhikingsuggestions.azurewebsites.net/
  
# Github link: 
  https://github.com/smithaeshwarahalliramesh/Personalized-Hiking-Suggestions
