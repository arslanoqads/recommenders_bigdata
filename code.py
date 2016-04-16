import pandas as pd
import matplotlib.pyplot as plt
import math
import scipy.stats as st
import data


movie_user_preferences=data.content


# find frame for two movies and all users
x=[]
for i in movie_user_preferences.keys():
    x.append((i,movie_user_preferences[i]['Django Unchained'],
                movie_user_preferences[i]['Avenger: Age of Ultron']))

df=pd.DataFrame(x,columns=['name','Django','Avenger'])




#plot 2 movies
plt.scatter(df['Django'],df['Avenger'])
plt.xlabel('Django')
plt.ylabel('Avenger')
for i, txt in enumerate (df.name):
    plt.annotate(txt,(df.Django[i],df.Avenger[i]))
    
    
# method to find the euclediean distance
# for any two people in data find the sum of squares    
def distance(prefs,person1,person2):
# Get the list of shared_items
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:    
            si[item]=1   
    if len(si)==0: return 0   # if they have no ratings in common, return 0
    # Add up the squares of all the differences of common movies 1 or more
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) 
                    for item in prefs[person1] if item in prefs[person2]])
    return 1/(1+sum_of_squares)    
    


# get dataframe of preferences of two users
def movie_user_df(input_data, user1, user2):
    data = []
    for movie in input_data[user1].keys():
        if movie in input_data[user2].keys():
            try:
                data.append((movie
                ,input_data[user1][movie]
                ,input_data[user2][movie]) )
            except:
                pass
    return pd.DataFrame(data = data, columns = ['movie', user1,
    user2])
    
df=movie_user_df(movie_user_preferences,'Jill','Max')



#plt.scatter(df.Jill,df.Max)
#for i,txt in enumerate (df.movie):
#    plt.annotate(txt,(df.Jill[i],df.Max[i]))


st.pearsonr(df.Jill,df.Max)
#below code does the same thing

# Returns the Pearson correlation coefficient for p1 and p2
def pearson(prefs,p1,p2):
# Get the list of mutually rated items
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    # Find the number of elements
    
    n=len(si)
    # if they are no ratings in common, return 0
    if n==0: return 0
    # Add up all the preferences for common movies
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    # Sum up the squares
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    # Sum up the products
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    # Calculate Pearson score
    num=pSum-(sum1*sum2/n)
    den=math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0
    r=num/den
    return r

pearson(movie_user_preferences,'Jill','Max')




#ranking pf 'person' with other people in the list
#returns top n people similar to you
def top_matches(prefs,person,n=5,similarity=pearson):
    # using the user specified distance function
    # score contains the (similarity,person) for all people 
    scores=[(similarity(prefs,person,other),other) #computes similarity with every other element
        for other in prefs if other!=person]
    # Sort the list so the highest scores appear at the top
    scores.sort( )
    scores.reverse( )
    return scores[0:n]
    
    
top_matches(movie_user_preferences,'Toby',n = 3, similarity = distance)    




# Gets recommendations for a person by using a weighted average
# of every other user's rankings
# get value for a movie X for all users (similarity, totals) and calculate ranking
def get_recommendations(prefs,person,similarity=pearson):
    totals={}
    simSums={}
    for other in prefs:    
        if other==person: continue # don't compare me to myself
        sim=similarity(prefs,person,other) #based on distance function        
        if sim<=0: continue  #ignore scores of zero or lower
        for item in prefs[other]: #pick movies from other preferences
            
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item]==0:
            # Similarity * Score
                print item,sim, other
               
                totals.setdefault(item,0) #initiate the value to 0
                totals[item]+=prefs[other][item]*sim # take sum of all rating x similarity
                
                # Sum of similarities
                simSums.setdefault(item,0)
                simSums[item]+=sim #take sum of all similarities among all people
               
                # Create the normalized list
    rankings=[(total/simSums[item],item) for item,total in totals.items( )]
    # Return the sorted list
    
    rankings.sort( )
    rankings.reverse( )
    return rankings
    
get_recommendations(movie_user_preferences,'Toby')

get_recommendations(movie_user_preferences,'Toby',
similarity = distance)    
    
"""
user based above, item based below

User-based collaborative filtering finds the similarities between users, 
and then using these similarities between users, a recommendation is made.

Item-based collaborative filtering finds the similarities between items. 
This is then used to find new recommendations for a user.

"""    

# To begin with item-based collaborative filtering, we'll first have to 
# invert our dataset by putting the movies in the first layer, followed 
# by the users in the second layer:
def transform_prefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            # Flip item and person
            result[item][person]=prefs[person][item]
    return result
        
    
inverted=transform_prefs(movie_user_preferences)

"""

def top_matches(prefs,outer_item,n=5,similarity=pearson):
    # using the user specified distance function
    # score contains the (similarity,outer_item) for all people 
    scores=[(similarity(prefs,outer_item,other),other)for other in prefs if other!=outer_item]
    # Sort the list so the highest scores appear at the top
    scores.sort( )
    scores.reverse( )
    return scores[0:n]

"""

#find similar elements
#for every outer_item(movie) match with all other outer_items
#return multiple values for distance/will all comparizons using top_matches method
def calculate_similar_items(prefs,n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result={}
    # Invert the preference matrix to be item-centric
    itemPrefs=transform_prefs(prefs)
    c=0
    for item in itemPrefs:
        # Status updates for large datasets
        c+=1
        # if c%100==0: print "%d / %d" % (c,len(itemPrefs))
        # Find the most similar items to this one
        #the simialarity function compares two sub_items (users here) based
        #based on eucledian/pearson.
        #top_matches does this comparison for all elements in the frame.
        scores=top_matches(itemPrefs, item, n=n,similarity=distance)
        result[item]=scores
    return result
    
itemsim=calculate_similar_items(movie_user_preferences)    

def get_recommendedItems(prefs,itemMatch,for_user):
    userRatings=prefs[for_user] #user
    scores={}
    totalSim={}
    # Loop over items rated by this user
    for (item,rating) in userRatings.items( ): #movie + rating
    # Loop user's watched movie and compare it with, the movie's similar movies using method.
        for (similarity,item2) in itemMatch[item]: #match in similiar movie calculated above
            if item2 in userRatings: continue # Ignore if this user has already rated this item
            # Weighted sum of rating times similarity
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            # Sum of all the similarities
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
    
    # Divide each total score by total weighting to get an average
    rankings=[(score/totalSim[item],item) for item,score in scores.items( )]
    # Return the rankings from highest to lowest
    rankings.sort( )
    rankings.reverse( )
    return rankings
 
#movie_user_preferences
    
    
get_recommendedItems(movie_user_preferences, itemsim,'Toby')    

plt.show()