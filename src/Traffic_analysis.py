import plotly.offline as pyo
import streamlit as st 
import plotly.express as px

def app():
    if 'df' in st.session_state:
        df = st.session_state.df
        print(df.columns)
#punkte variable in der Größe
        fig = px.scatter(
        data_frame=df,
        x = 'gdpPercap',
        y = 'lifeExp',
        size ='pop',
        color='continent',
        log_x = True,
        title ='Entwicklung von traffic über Zeit',
        hover_name= 'Bezirk',
        labels = {'gdpPercap': 'GDP pro Kopf'},
        # labels =dict(gdpPercap= 'GDP pro Kopf', lifeExp= 'Lebenserwartung'),
        animation_frame= 'year' ,
        animation_group='country',
        size_max= 60  # Geschwindigkeit steuern 
    )
    fig.show()
    #st.plotly_chat : show in combination plotlyexpress mit streamlit
    pyo.plot(fig)