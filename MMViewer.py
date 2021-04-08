import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import GoogleV3 #cannot store goole API data longer then 30 days
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

import os

fixsoidonthavetolearnsomethingnew = os.path.normpath('C:/Users/Talapoin/Desktop/Data_Science/MMdata/generateReqs/APIKey.txt')
with open(fixsoidonthavetolearnsomethingnew) as f:
    lines = f.readlines()
key=lines[0]


#Function Definitions
#---------------------------------------------------------------------------------------------------------------------------------------
def readandclean(file_path):
    df = pd.read_csv(file_path,header = None)   #temporary workaround is to process data in the notebook and then write to streamlit.csv #this should not read in headers!!
    df = df.rename(columns={0:'Name',1:'cust #',9:'Address 1',10:'City',11:'State',12:'Zip',14:'theMotherLode'})
    df=df.dropna(how='all')
    df=df.drop(len(df)-1)
    df["cust #"].fillna(0, inplace = True) 
    df['cust #']=df['cust #'].astype('int64')
    update=df[['cust #','Name','Address 1','City','State','Zip','theMotherLode']]
    Statenull=update[update['State'].isnull()]
    update["State"].fillna('MN', inplace = True) 
    Zipnull=update[update['Zip'].isnull()]
    update['location'] = '0'
    for i in range(len(update['location'])):
        update['location'][i] = str(update['Address 1'][i]) +' '+ str(update['City'][i]) + ', ' + str(update['State'][i]) 
    return(update)

    
def cachemeousside(update):
    cache = pd.read_csv(r'C:\Users\Talapoin\Desktop/Data_Science\MMdata\cache.csv')
    cache = cache[['cust #','cachelocation','latitude','longitude']]
    for i  in range(len(update)):
        custID = update['cust #'][i] 
        try: #if cust # does not exist in cache, the exception adds the cust # into the cache with 0 data
            testfunctionpleasedontprint=cache['cust #'].loc[cache['cust #']==custID].values[0]
            cache['cachelocation'].loc[cache['cust #']==custID] = update['location'][i]
        except:
            custID = {"cust #":custID}#,"cachelocation":'none',"latitude":0,"longitude":0}
            custID=pd.DataFrame(custID, index = [0])
            cache = cache.append(custID, ignore_index=True)
            addedtocache = addedtocache+1    
            cache['cachelocation'].loc[cache['cust #']==custID] = update['location'][i]
    return(cache)

@st.cache
def findlocation(update,cache,key):
    update = update[['cust #','Name','Address 1','City','State','Zip','location']]
    update=update.merge(cache, how = "left",on ='cust #')#searches based on cust # and adds latitude and longitude
    x = 0
    aa = 0
    pc = 0
    lnc = 0
    t = 0
    cc = 0
    testfunctionpleasedontprint=0
    addedtocache = 0
    addresslist = list()
    custIDlist = list()
    errorlist = list()
    geolocator = GoogleV3(api_key=key)
    for i  in range(len(update)):
        custID = update['cust #'][i] #if there is a new cust #, set cache address to some rando string.
        prior = float(cache['latitude'].loc[cache['cust #']==custID].values) #goofy way to get the latitude based on cust# and specifically not use index
        cacheaddress = cache['cachelocation'].loc[cache['cust #']==custID].to_string()[7:500]
        address = update['location'][i]
        if address==cacheaddress: #if address is the same as previous cache address, skip everything.
            aa = aa + 1
        else:
            if prior == 0:    
                location = geolocator.geocode(address)
                pc = pc+1
                if location == None:
                    x = x+1
                    update['latitude'].loc[i] = 0 #fill in 0 if geolocator finds nothing.
                    update['longitude'].loc[i] = 0 
                    lnc = lnc+1
                    errorlist = custID
                else:
                    update['latitude'].loc[i] = location.latitude #geolocator found lat and lon.
                    update['longitude'].loc[i] = location.longitude
                    cache['latitude'].loc[cache['cust #']==custID] = location.latitude
                    cache['longitude'].loc[cache['cust #']==custID] = location.longitude
                    
                    t = t+1
            else:              
                update['latitude'].loc[i] = cache['latitude'].loc[cache['cust #']==custID].values#cache['latitude'].loc[cache['cust #']==custID]  #some sort of issue here|||||||||||||||||||||||||||||||||||||||||
                update['longitude'].loc[i] = cache['longitude'].loc[cache['cust #']==custID].values  
                cc = cc+1
                addresslist.append(address)
                custIDlist.append(custID)
    cache.to_csv(r'C:\Users\Talapoin\Desktop/Data_Science\MMdata\cache.csv',index=False)
    return(update)

def findneighbors(user_input,dataframe):
    featuresC = dataframe[["latitude","longitude"]] #disctance data. X and y locations
    scaleC = StandardScaler() #create the scaling object
    scaled_featuresC = scaleC.fit_transform(featuresC) #scales the latitude and longitude values.
    index = dataframe.loc[dataframe["Name"]==user_input].index #program finds the index
    userinputindex = scaled_featuresC[index] #index is used to find correct scaled value
    neigh = NearestNeighbors(n_neighbors = 8)
    neigh.fit(scaled_featuresC)
    mystuff=neigh.kneighbors(userinputindex, 8, return_distance=False)#scaled value input into nearest neighbors algorithm
    mystuffinalist=mystuff.tolist()
    showdf = pd.DataFrame(columns = dataframe.columns)
# use indices of each one to form dataframe countaining cust #, name, location
    for i in range(len(mystuffinalist[0])):
        x = mystuffinalist[0][i] #get first index out of list.
        showdf=showdf.append(dataframe.iloc[x],ignore_index=True) #use index to find the relevant data and append to showdf dataframe.

    showdf=showdf[["cust #","Name", "location"]]
    showdf=showdf.rename(columns = {"cust #":"Customer Number","location":"Customer Address"})
    return(showdf)
#---------------------------------------------------------------------------------------------------------------------------------------



#-------------------------Title and subtitle---------------------------
#Styler.apply(update[update['location'].str.match('.*[0-9].*')== False], axis=None) APPLY THIS TO SHOWDF
def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val.str.match('.*[0-9].*')== False else 'black'
    return 'color: %s' % color



header= st.header("Welcome to the M and M Scheduling Helper!")
subheader = st.subheader("name is...up for debate")
st.markdown('[Instructions for downloading new data](https://docs.google.com/document/d/1aulnfdU-DXfOeIkTlp-qzSxdS2ZMSdm7crS4-RjAPWc/edit?usp=sharing)')
file_path = st.file_uploader(label='Upload new .csv file')
#file_path = r'C:\Users\Talapoin\Desktop/Data_Science\MMdata\328.csv' contigency plan
left_column, right_column = st.beta_columns(2)


update = readandclean(file_path) #must be unaltered CSV file. file_path.name may also work.
cache = cachemeousside(update)
update = findlocation(update,cache,key)


baddata = update[update['location'].str.match('.*[0-9].*')== False] # Isolates out locations that do not contain numbers.  address should have a number


clients = np.sort(update['Name'].unique()) #sorts the names of the clients into alphabetical order and removes duplicates.
user_input = st.sidebar.selectbox('Search by Customer name', clients) #user inputs name of client
showdf = findneighbors(user_input,update)

#showdf = showdf['Customer Address'].styler.apply(color_negative_red)
st.table(showdf)

#--------------------------Button--------------------------------
pressed = left_column.button('Press me?')
if pressed:
    left_column.markdown("M & M is the best! :sunglasses:")

    
    
#-------------------missing client expander---------------------
issues = len(baddata.index)
issues = str(issues)+" Locations have potentially bad data."
expander = st.beta_expander(issues)
expander.table(baddata)


 
    
    
    
    
    
    
    

    
    







