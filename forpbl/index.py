import streamlit as st
import pandas as pd
import numpy as np
import csv
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

st.title('住みやすい街検索')
st.write('### test')

@st.cache
def lord(filename):
    content = np.loadtxt(filename, delimiter=',', skiprows=1,)
    return content

@st.cache
def neighbourhood(p0, ps):
    L = np.array([])
    for i in range(ps.shape[0]):
        norm = np.sqrt( (ps[i][1] - p0[0])*(ps[i][1] - p0[0]) +
                        (ps[i][2] - p0[1])*(ps[i][2] - p0[1]) )
        L = np.append(L, norm)
    return ps[np.argmin(L)]

@st.cache
def coordinate(address):
    """
    addressに住所を指定すると緯度経度を返す。

    >>> coordinate('東京都文京区本郷7-3-1')
    ['35.712056', '139.762775']
    """
    URL = 'http://www.geocoding.jp/api/'
    payload = {'q': address}
    html = requests.get(URL, params=payload)
    soup = BeautifulSoup(html.content, "html.parser")
    if soup.find('error'):
        raise ValueError(f"Invalid address submitted. {address}")
    latitude = soup.find('lat').string
    longitude = soup.find('lng').string
    return [longitude, latitude]

with st.sidebar:
    with st.form(key='input'):
        st.title('検索')
        address = st.text_input("住所入力（部分一致）", "新宿区")
        run = st.form_submit_button('Run')


if run:
    data_load_state = st.text('Loading data...')
    longlat = (coordinate(address))
    longlat_float = [float(n) for n in longlat]
    content_ndvi = np.array(lord("data/NDVI_Japan.csv"))
    content_air = np.array(lord("data/air_Japan.csv"))
    nearrest_coor_ndvi  = neighbourhood(longlat_float, content_ndvi)
    nearrest_coor_air  = neighbourhood(longlat_float, content_air)
    nearrest_longlat = {
     'lon' : [longlat_float[0]],
     'lat' : [longlat_float[1]]
    }
    # st.write(longlat_float)
    # st.write((nearrest_coor_ndvi[1], nearrest_coor_ndvi[2], nearrest_coor_ndvi[3]))
    st.write("## 植生スコア : {}　空気スコア : {}".format(nearrest_coor_ndvi[3], nearrest_coor_air[2]))
    st.bar_chart({
    "スコア": [nearrest_coor_ndvi[3], nearrest_coor_air[2]],
    # "空気スコア": [nearrest_coor_air[2]]
    })
    map_data = pd.DataFrame(nearrest_longlat)
    st.map(map_data)
    data_load_state.success("Success!!")
