def app():
    import streamlit as st
    import folium
    from folium.plugins import MarkerCluster
    import pandas as pd
    from streamlit_folium import folium_static

    # Load data
    df = pd.read_excel("../data/processed/Tableau Standort PKW.xlsx")
    df_Zählstationen = pd.read_excel("../data/processed/Tableau Excel Fahrrad.xlsx")
    
    # Create the map centered around the average latitude and longitude
    m = folium.Map(location=[df['BREITENGRAD'].mean(), df['LÄNGENGRAD'].mean()], zoom_start=13)

    # Add MarkerCluster for PKWs
    marker_cluster = MarkerCluster(name="Messstationen PKWs").add_to(m)
    for index, row in df.iterrows():
        popup_html = f"""
        <html>
        <head>
            <style>
                .popup {{
                    font-size: 14px;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                    border: 2px solid #ccc;
                }}
                .popup-title {{
                    font-weight: bold;
                    color: #2a2a2a;
                }}
                .popup-count {{
                    color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="popup">
                <p class="popup-title">{row['MQ_KURZNAME']}</p>
                <p class="popup-count">{row['Anzahl Zählungen']} PKWs</p>
            </div>
        </body>
        </html>
        """
        folium.Marker(
            location=[row['BREITENGRAD'], row['LÄNGENGRAD']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    # Add MarkerCluster for Fahrräder
    marker_cluster_new = MarkerCluster(name="Zählerstelle Fahrräder").add_to(m)
    for index, row in df_Zählstationen.iterrows():
        popup_html = f"""
        <b>Messstation:</b> {row['Zählstelle']}<br>
        <b>Zählungen:</b> {row['Anzahl Messungen']}<br>
        """
        folium.Marker(
            location=[row['Breitengrad'], row['Längengrad']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(marker_cluster_new)

    # Add a layer control to toggle MarkerClusters
    folium.LayerControl().add_to(m)

    # Center map in Streamlit using custom CSS
    st.markdown(
        """
        <style>
        .map-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Streamlit UI
    st.title("Geografische PKWs Messstationen auf der Karte")
    st.write("Diese Karte zeigt die Messstationen mit ihren jeweiligen Zählwerten.")
    
    # Add the map inside a centered container
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    folium_static(m, width=900, height=600)
    st.markdown('</div>', unsafe_allow_html=True)