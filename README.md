The goal of this script is to create an interface that can be used by any non-programmer to find 
the 8 nearest neighbors to a particular customer.  

One of the largest challenges facing home service small businesses is scheduling customers and attempting to 
minimize the drving distance from one client to another in a day.  A poorly created schedule could have a 
technician drive up to 3 hours around the city for these 8 jobs. An added wrinkle to this problem is that 
pest control scheduling can be largely impromptu.  As with many at home service industries, there is 
a level of emergency when a customer calls.

This is accomplished by utilizing the Streamlit framework for a friendly user interface, Geopy and Google's Geolocation 
API for customer locations,  and the SciKitlearn package for the nearest neighbor algorithm. This script is currently
configured to be used with data exported from the RDF Pest Control software, (https://www.rdfsoftware.com/). 

In order to use this script, a user would need a google API key stored locally in addition to having the necessary 
data exported from an RDF database.  

This script has not been uploaded in a form that is usable due to the sensitive nature of my personal API key and 
the customer list of a small pest control company.





