#!/usr/bin/env python
# coding: utf-8

# # MAPAS DE INCIDENCIA POSITIVOS SARS-COV-2

import pandas as pd
import geopandas as gpd
import branca.colormap as cm
import folium
from datetime import datetime
import numpy as np


def genera_municipios():
    archivo_poligonos = '../data/raw/poligonos_sonora.geojson'
    gdf_poligonos = gpd.read_file(archivo_poligonos)
    return gdf_poligonos['Municipio']

def mapa_mun_son(df, titulo, etiqueta="Información", indices=None, colores=None, filename=None):
    """
    Hace un mapa de Sonora de cloropetos
    df: Dataframe con dos variables: 'Municipios' y 'Data'
        donde:
            Municipios en la lista "genera_municipios()"
            Data el dato que queremos graficar
    titulo: string con el titulo de la barra
    indices: [i0, ..., imax] los valores posibles. Si es un entero entonces
             range(0:max(Data):indices)
    colores: [(r, g, b), (r, g, b), ... (r, g, b)] una lista con colores
             del mismo tamaño que indice. Si None toma la que tenemos por default (4 valores)
             
    filename = str (un nombre sin extensión), si None, entonces no se guarda archivo.
    
    """

    archivo_poligonos = '../data/raw/poligonos_sonora.geojson'
    gdf_poligonos = gpd.read_file(archivo_poligonos)
    gdf_poligonos = gdf_poligonos.merge(df, on='Municipio', how='outer')


    v_max = gdf_poligonos['Data'].max()
    if indices == None:
        indices = np.linspace(0, v_max, 5).tolist()
    elif type(indices) == type(3):
        indices = list(range(0, v_max, indices))
    
    if colores == None or indices == None:
        colores = [(255, 215, 0),(124, 252, 0),(180, 60, 66),(128, 0, 128),(25, 25, 112)]
    
    step_no_uniforme_lineal = cm.LinearColormap(colors=colores, index=indices, vmin=0, vmax=v_max)
    step_no_uniforme_discreta = cm.StepColormap(colors=colores, index=indices, vmin=0, vmax=v_max)


    #Se crea un mapa apuntando a Sonora
    m = folium.Map(
        tiles = 'cartodbpositron', 
        location=[29.3333300,  -110.6666700], 
        zoom_start=7
    )

    #Se crea una serie con la información de los municipios para construir una función de estilo
    data_serie = df.set_index('Municipio')['Data']

    #Se crea una serie con la información de los municipios para construir una función de estilo
    data_dict = df.set_index('Municipio')['Data'].to_dict()

    def style_function(feature):
        valor = data_dict.get(feature['properties']['Municipio'])
        return {
            'fillOpacity': 0.1 if valor is None else 1 ,
            'weight': 1,
            'fillColor': '#gray' if valor is None else step_no_uniforme_lineal(valor)
        }

    #Agregamos al mapa los polígonos con sus respectivos estilos
    folium.GeoJson(
        data=gdf_poligonos.to_json(),
        style_function=style_function
    ).add_to(m)

    #Después, agregamos la barra de colores con su leyenda
    step_no_uniforme_lineal.caption = titulo
    m.add_child(step_no_uniforme_lineal)

    #Estas funciones auxiliares son para definir el estilo que tomarán los polígonos
    #al pasar el mouse por encima de ellos
    style_function = lambda x: {
        'fillColor': '#ffffff',
        'color':'#000000',
        'fillOpacity': 0,
        'weight': 1
    }
    highlight_function = lambda x: {
        'fillColor': '#000000',
        'color':'#000000',
        'fillOpacity': 0.30,
        'weight': 0.1
    }

    #Se agrega la capa que se encargará de desplegar la información de los polígonos
    NIL = folium.features.GeoJson(
        data=gdf_poligonos.to_json(),
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Municipio', 'Data'],
            aliases=['Municipio: ', etiqueta+': '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    m.add_child(NIL)
    m.keep_in_front(NIL)

    if filename != None:
        m.save(f'{filename}.html')

    return m
