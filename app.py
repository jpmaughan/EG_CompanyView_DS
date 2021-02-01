# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 09:47:04 2021

@author: MaughanJ1
"""

import streamlit as st
import pandas as pd
import folium
import shapefile
from shapely.geometry import Polygon
from streamlit_folium import folium_static
from shapely.ops import cascaded_union
import geopandas as gpd
#from streamlit_folium import folium_static
from pyproj import Proj, transform


inProj = Proj(init='epsg:27700')
outProj = Proj(init='epsg:4326')

save_path = 'C:/Users/maughanj1/Documents/EGDS/EGDS-194 DataDiscovery/EGDS-195 LandRegistry_OCOD_CCOD/data/Dash/'
df_uprn = pd.read_csv(save_path + 'tbl_uprns_sample.csv')
df_rdx = pd.read_csv(save_path + 'tbl_rdx_sample.csv')
df_lr_ownership = pd.read_csv(save_path + 'tbl_lr_sample.csv')
df_abp_cr_voa = pd.read_csv(save_path + 'tbl_abp_sample.csv')
df_voa1 = pd.read_csv(save_path + 'tbl_voa1_sample.csv')
df_voa2 = pd.read_csv(save_path + 'tbl_voa2_sample.csv')


uprn_choice = st.selectbox("UPRN Choice :: ", options=list(df_uprn.UPRN.unique()))
st.write(' ')
st.write('Good Example :: 49316')
st.write('Bad UPRN Matching Example :: 49316')
st.write('-------------')
st.write(' ')


df_uprn_example = df_uprn.loc[df_uprn.UPRN == int(uprn_choice)]
title_numb_example = list(df_uprn_example.TITLE_NO.unique())
df_rdx_example = df_rdx.loc[df_rdx.address_uprn == int(uprn_choice)]
df_lr_own_example = df_lr_ownership.loc[df_lr_ownership['Title Number'].isin(title_numb_example)]
df_abp_cr_voa_example = df_abp_cr_voa.loc[df_abp_cr_voa.UPRN == int(uprn_choice)]
list_uarns = list(df_abp_cr_voa_example.CROSS_REFERENCE.unique())
df_voa1_example = df_voa1.loc[df_voa1.UARN.isin(list_uarns)]
df_voa2_example = df_voa2.loc[df_voa2.UAN.isin(list_uarns)].drop_duplicates(['Line']).sort_values(['Floor'], ascending=False)

st.write(' ')
st.write("Preffered Display Address :: ", df_rdx_example.preferredDisplayAddress.values[0])
st.write("Radius Address :: ", df_rdx_example.address_fullAddress.values[0])
st.write('-----------')


## Shapefile read 
sf_path = 'C:/Users/maughanj1/Documents/EGDS/EGDS-9 Unassigned/EGDS-147 NationalPolygons/LR_NPS_SAMPLE/'
sf = shapefile.Reader(sf_path + "LR_POLY_SAMPLE.shp")

columns_names = [i[0] for i in sf.fields[1:]]
columns_names.append('SHAPEFILE')

df_shapefiles = pd.DataFrame(columns=columns_names)
n=0

## Folium 
crs = {'init': 'epsg:27700'}

lat = df_rdx_example.address_latitude.values[0]
lon = df_rdx_example.address_longitude.values[0]
m = folium.Map(location=(float(lat),float(lon)), zoom_start=18)
folium.Marker([lat,lon], tooltip="UPRN ::" + str(uprn_choice)).add_to(m)

for i, j in zip(sf.iterRecords(), sf.iterShapes()):
    if i[1] in title_numb_example:
        poly_points = []

        for point in j.points:
            #print(point)
            x1, y1 = point
            x2, y2 = transform(inProj,outProj,x1,y1)
            #print(x2, y2)
            poly_points.append((x2,y2))        
        folium.GeoJson(Polygon(poly_points)).add_to(m)     
        i.append(Polygon(j.points))
        df_shapefiles.loc[n] = i
        n += 1 


folium_static(m)





polygon_geom = cascaded_union(df_shapefiles.SHAPEFILE.values)
polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])

st.write('Polygon Area :: ', polygon.area[0], ' :: Unit  Unknown')


# =============================================================================
# for tn in title_numb_example:
#     df_sf = df_shapefiles.loc[df_shapefiles.TITLE_NO == tn]
#     u = cascaded_union(df_sf.SHAPEFILE.values)
#     polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[u])
#     folium.GeoJson(polygon.geometry).add_to(m)
#     
# =============================================================================


## Rerun for the OS Map
# =============================================================================
# 
# from osm_runner import Runner
# runner = Runner()
# 
# lat1, lon1 = (lat - 0.00005, lon - 0.00005)
# lat2, lon2 = (lat + 0.00005, lon + 0.00005)
# bg_str = f"({lat1},{lon1},{lat2},{lon2})"
#     
# df_osm = runner.gen_osm_df('polygon', bg_str)
# 
# m = folium.Map(location=(float(lat),float(lon)), zoom_start=18)
# folium.Marker([lat,lon]).add_to(m)
# 
# df_plot = df_osm.copy()
# df_plot.fillna('', inplace=True)
# 
# for row in df_plot.iterrows():
#     row = row[1]
#     
#     sf = row['geom']#.values[0]
#     #name = row['name'] 
#     #building_levels = row['building']
#     #land_use = row['landuse']
#     #full_string = name + ' : ' + building_levels + ' : ' + land_use
#     folium.GeoJson(sf.JSON).add_to(m)
#     
# folium_static(m)
# 
# st.write('Open Street Map')
# st.write(df_osm.drop(['geom'],axis=1).fillna(''))
# =============================================================================

# call to render Folium map in Streamlit

st.write('-------------')
st.write(' ')
st.write(' ')

st.write('National Polygon Dataset')
st.write(df_uprn_example)

radius_cols = ['Record_Type','unit_totalSpace_value','unit_totalSpace_measurement','unit_primaryUseType','lease_tenant_company_name','sale_purchasers_0_company_name']

st.write('Radius Deals')
st.write(df_rdx_example[radius_cols].fillna(''))

land_reg_cols = [ 'Title Number', 'Tenure', 'Property Address', 'Postcode',  'Price Paid', 'Proprietor Name (1)',
       'Company Registration No (1)']

st.write('Land Reg Ownership')
st.write(df_lr_own_example[land_reg_cols])


# =============================================================================
# abp_cols = []
# 
# st.write('AddressBasePremium :: CrossRef')
# st.write(df_abp_cr_voa_example)
# =============================================================================

voa1_cols = ['FirmsName', 'NumberOrName','Street', 'Town','PrimaryDesc', 'TotalArea',
       'SubTotal', 'TotalValue','FromDate', 'ToDate']

st.write('VOA_1 :: Summary')
st.write(df_voa1_example[voa1_cols])

voa2_cols = ['RecordType', 'Line', 'Floor', 'Description',
       'Area', 'Price', 'Value']

st.write('VOA_2 :: Breakdown')
st.write(df_voa2_example[voa2_cols])