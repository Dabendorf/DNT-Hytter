#!/usr/bin/env python
# coding: utf-8

# In[98]:


import os
import json
import pandas as pd
import folium
import gpxpy
import gpxpy.gpx
import requests
import math


# If this value is true, the programme will fetch the data again from the ut.no API. Set this to false if you want to play around with the code.
# 
# Then the programme will get its data from a cached version in the data folder

# In[99]:


fetch_data_from_api_again = True


# ### Helper functions

# In[100]:


# Read and combine all json files
def read_json_files(folder_path):
    combined_edges = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                data = json.load(file)
                edges = data["data"]["ntb_findCabins"]["edges"]
                combined_edges.extend(edges)
    return combined_edges


# In[101]:


# Convert data into pandas dataframe
def convert_to_dataframe(data):
    records = []
    for item in data:
        node = item["node"]
        geometry = node["geometry"]
        record = {
            "id": node["id"],
            "name": node["name"],
            "serviceLevel": node["serviceLevel"],
            "dntCabin": node["dntCabin"],
            "ownername": node["owner"]["name"],
            "latitude": geometry["coordinates"][1],  # longitude
            "longitude": geometry["coordinates"][0],  # latitude
            "height": geometry["coordinates"][2],  # height
            "areaName": node["areas"][0]["name"] if node["areas"] else "",  # area name
            "dntKey": node["openingHours"][0]["key"] if node["openingHours"] else "",
            "bedsStaffed": node["bedsStaffed"],
            "bedsNoService": node["bedsNoService"],
            "bedsSelfService": node["bedsSelfService"],
        }
        records.append(record)
    df = pd.DataFrame(records)
    return df


# In[102]:


def getCounterTable(df: pd.DataFrame, column_name: str, sort_ascending=False):
	counts = df[column_name].value_counts()

	sorted_counts = counts.sort_values(ascending=sort_ascending)

	return pd.DataFrame({'Value': sorted_counts.index, 'Count': sorted_counts.values})


# ### Download from UT.no sin API

# #### Static data
# The API only allows the download of up to 500 huts at the same time. Therefore one needs to trigger the API several times.
# 
# At the moment, the number of huts is 645 (2024-03-15), so it will hardly be necessary to do more than 2 times in the future.
# 
# However, there is a static value being set to 500 and an automatism checking if there is more data later.
# 
# If this somehow does not work, try to change the static number, they might have changed the maximum

# In[103]:


request_huts_per_request = 500
folder_path = './data/'


# In[104]:


more_data_available = fetch_data_from_api_again
counter_pagination = 0
afterCursor = None

while more_data_available:
    post_data = {
        "operationName": "FindCabins",
        "variables": {
            "input": {
                "pageOptions": {
                    "limit": request_huts_per_request,
                    "afterCursor": afterCursor,
                    "orderByDirection": "DESC",
                    "orderBy": "ID",
                },
                "filters": {"and": [{"dntCabin": {"value": True}}]},
            }
        },
        "query": "query FindCabins($input: NTB_FindCabinsInput) {\n  ntb_findCabins(input: $input) {\n    totalCount\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    edges {\n      node {\n        ...CabinFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CabinFragment on NTB_Cabin {\n  id\n  name\n  serviceLevel\n  bedsToday\n  bedsStaffed\n  bedsNoService\n  bedsSelfService\n  bedsWinter\n  dntCabin\n  owner {\n    name\n    __typename\n  }\n  accessibilities {\n    id\n    name\n    __typename\n  }\n  openingHours {\n    allYear\n    from\n    to\n    serviceLevel\n    key\n    __typename\n  }\n  geometry\n  media {\n    id\n    uri\n    type\n    description\n    tags\n    __typename\n  }\n  areas {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n",
    }

    p_data = json.dumps(post_data)
    ua = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0'

    # Make post request
    dnt_hytter_response = requests.post(
        "https://api.ut.no",
        data=p_data,
        headers={"Content-Type": "application/json", "User-Agent": ua},
    )

    if dnt_hytter_response.headers.get('content-type') == 'application/json':
        response_data = dnt_hytter_response.json()
    else:
        response_data = None

    
    page_info = response_data["data"]["ntb_findCabins"]["pageInfo"]

    json_obj = json.dumps(dnt_hytter_response.json(), indent=4)

    with open(f"{folder_path}hytter_{counter_pagination}.json", "w") as outfile:
        outfile.write(json_obj)

    if page_info["hasNextPage"]:
        counter_pagination += 1
        afterCursor = page_info["endCursor"]
    else:
        more_data_available = False


# ### Read json files

# In[105]:


combined_data = read_json_files(folder_path)


# ### Convert to pandas

# In[106]:


df = convert_to_dataframe(combined_data)


# ### Check length
# Was 645 on 2024-03-15, should be "similar" at any later point

# In[107]:


len(combined_data)


# ### Show table

# In[108]:


df


# #### Prefilter
# This applies filters to the table before anything else will happen. The standard code only has one filter.
# It removes all huts where one cannot stay overnight, like emergency shelters

# In[109]:


df = df[~df['serviceLevel'].isin(["emergency shelter", "food service", "no-service (no beds)", "closed"])]


# In[110]:


df


# In[111]:


df.sort_values(by=['areaName']).to_csv(f"{folder_path}alle_hytter.csv")


# ### Generate map

# In[112]:


m = folium.Map(location=[60.472, 8.468], zoom_start=6)

# Add markers for each point in the DataFrame
for i, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['name'],
        tooltip=f"Height: {row['height']} meters"
    ).add_to(m)

# Display the map
m.save(f"{folder_path}map_norway.html")  # Save the map to an HTML file


# In[113]:


m


# In[114]:


### Map Vestlandet (Norway most important region)


# In[115]:


m_vest = folium.Map(location=[60.170, 6.971], zoom_start=8)
# Add markers for each point in the DataFrame
for i, row in df.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['name'],
        tooltip=f"Height: {row['height']} meters"
    ).add_to(m_vest)

# Display the map
m_vest.save(f"{folder_path}map_vestlandet.html")  # Save the map to an HTML file


# In[116]:


m_vest


# ### Export to GPX file

# In[117]:


gpx = gpxpy.gpx.GPX()

# Create a GPX waypoint for each row in the DataFrame
for i, row in df.iterrows():
    waypoint = gpxpy.gpx.GPXWaypoint(latitude=row['latitude'], longitude=row['longitude'], elevation=row['height'])
    waypoint.name = row['name']

    gpx.waypoints.append(waypoint)

# Save the GPX to a file
with open(f"{folder_path}points.gpx", 'w') as f:
    f.write(gpx.to_xml())


# ### Statistics for nerds

# In[118]:


df


# ##### Service level (betjent, selv-betjent, ubetjent)

# In[119]:


getCounterTable(df, "serviceLevel")


# ##### Region

# In[120]:


getCounterTable(df, "areaName").head(20)


# ##### Owner (Is DNT or not)

# In[121]:


getCounterTable(df, "dntCabin")


# In[122]:


getCounterTable(df, "ownername")


# ##### DNT-Nøkkel neaded

# In[123]:


getCounterTable(df, "dntKey")


# In[ ]:




