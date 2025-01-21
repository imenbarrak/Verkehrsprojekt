import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

#df_mess_auto = pd.read_csv('../data/processed/MessDatenAuto.csv').reset_index()
#df_mess_fahrrad = pd.read_csv('../data/processed/MessDatenFahrrad.csv').reset_index()

def app():
    
    # Check if data is loaded in session state
    #print(st.session_state)
    
    
    if 'df_pkws' in st.session_state and 'df_Fahrräder' in st.session_state :
        df_pkws = st.session_state.df_pkws
        df_Fahrräder = st.session_state.df_Fahrräder


        st.header("Data korrelation")
        numerical_columns = ['temperature_2m (°C)', 'relative_humidity_2m (%)', 
                     'rain (mm)', 'snowfall (cm)', 'cloud_cover (%)']

        # Calculate correlation matrix
        corr_matrix_pkws = df_pkws[numerical_columns+['q_pkw_mq_hr']].corr()
        corr_matrix_fahrräder = df_Fahrräder[numerical_columns+['Wert']].corr()
        
        col1, col2 = st.columns(2)
        with col1:
        #plt.figure(figsize=(10, 6))
            # Plot the heatmap
            sns.heatmap(corr_matrix_fahrräder, annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Correlation Heatmap Fahrräders')
            st.pyplot(plt)  # Display the plot
            plt.clf()
            
        with col2:
            # Plot the heatmap
            sns.heatmap(corr_matrix_pkws, annot=True,  fmt='.2f')
            plt.title('Correlation Heatmap PKWs')
            st.pyplot(plt)  # Display the plot
            plt.clf()
        
        
        
        st.header("PKWs vs Fahrräder Nutzung im Laufe der Zeit")
        # Ensure 'Date' is in datetime format
        # Ensure 'Date' is in datetime format for both dataframes
        df_pkws['Date'] = pd.to_datetime(df_pkws['Date'], format='%d.%m.%Y')
        df_Fahrräder['Date'] = pd.to_datetime(df_Fahrräder['Date'], format='%d.%m.%Y')

        # Add 'year' and 'quarter' columns to both dataframes
        df_pkws['year'] = df_pkws['Date'].dt.year
        df_pkws['quarter'] = df_pkws['Date'].dt.quarter

        df_Fahrräder['year'] = df_Fahrräder['Date'].dt.year
        df_Fahrräder['quarter'] = df_Fahrräder['Date'].dt.quarter

        # Group by year and quarter for both datasets
        quarterly_traffic_pkws = (
            df_pkws.groupby(['year', 'quarter'])['q_pkw_mq_hr']
            .mean()
            .reset_index()
        )

        quarterly_traffic_fahrrad = (
            df_Fahrräder.groupby(['year', 'quarter'])['Wert']
            .mean()
            .reset_index()
        )

        # Combine year and quarter into a single column for x-axis labels
        quarterly_traffic_pkws['year_quarter'] = (
            quarterly_traffic_pkws['year'].astype(str) + '-Q' + quarterly_traffic_pkws['quarter'].astype(str)
        )

        quarterly_traffic_fahrrad['year_quarter'] = (
            quarterly_traffic_fahrrad['year'].astype(str) + '-Q' + quarterly_traffic_fahrrad['quarter'].astype(str)
        )

        # Plot the data using Plotly Express
        fig = px.line(
            quarterly_traffic_pkws,
            x='year_quarter',
            y='q_pkw_mq_hr',
            title='Quarterly Traffic Volume: PKWs vs Fahrräder',
            labels={'year_quarter': 'Year-Quarter'},
            markers=True,
            line_shape='linear'
        )

        # Add the second line (df_Fahrräder data) to the same plot
        fig.add_scatter(
            name = 'Fahrräder',
            x=quarterly_traffic_fahrrad['year_quarter'],
            y=quarterly_traffic_fahrrad['Wert'],
            mode='lines+markers',
            line=dict(color='red')
        )

        # Customize the layout
        fig.update_layout(
            xaxis=dict(title='Year-Quarter', tickangle=45),
            yaxis=dict(title='Traffic Volume'),
            template='plotly_white',
            hovermode="x unified",  # Tooltip shows values for the current x-axis point
            legend_title="Legend",  # Title for the legend
            showlegend=True  # Ensure legend is visible
        )

        # Show the plot in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
        df_pkws['Date'] = pd.to_datetime(df_pkws['Date'], format='%d.%m.%Y')
        df_Fahrräder['Date'] = pd.to_datetime(df_Fahrräder['Date'], format='%d.%m.%Y')
        #df_pkws['Date'] = pd.to_datetime(df_pkws['Date'], format='%d.%m.%Y', errors='coerce')
        #df_mess_fahrrad['Date'] = pd.to_datetime(df_mess_fahrrad['Date'], format='%d.%m.%Y', errors='coerce')
        if 'year' in st.session_state:
            year = st.session_state.year
            df_pkws = df_pkws[(df_pkws['Date'].dt.year == year)]
            df_Fahrräder = df_Fahrräder[(df_Fahrräder['Date'].dt.year == year)]

        if 'month' in st.session_state:
            month = st.session_state.month
            df_pkws = df_pkws[(df_pkws['Date'].dt.month == month)]
            df_Fahrräder = df_Fahrräder[(df_Fahrräder['Date'].dt.month == month)]
            
        # if 'bezirk' in st.session_state:
        #     bezirk = st.session_state.bezirk
        #     df_pkws = df_pkws[(df_pkws['Bezirk']== bezirk)]
        #     df_Fahrräder = df_Fahrräder[(df_Fahrräder['Bezirk']== bezirk)]
    
        # Extract the calendar week from 'Date' column
        df_pkws['week'] = df_pkws['Date'].dt.isocalendar().week
        df_Fahrräder['week'] = df_Fahrräder['Date'].dt.isocalendar().week

        # Aggregate the 'q_pkw_mq_hr' column by week
        weekly_df_pkw = df_pkws.groupby('week').agg({'q_pkw_mq_hr': 'mean'}).reset_index()
        weekly_df_fahrrad = df_Fahrräder.groupby('week').agg({'Wert': 'mean'}).reset_index()
    
        fig = go.Figure()

        # Add the line plot
        fig.add_trace(go.Scatter(
            x=weekly_df_pkw['week'], 
            y=weekly_df_pkw['q_pkw_mq_hr'],
            mode='lines',  # 'lines' mode for line chart
            name='Mean Wert PKW',
            line=dict(color='blue') 
            
        ))
        fig.add_trace(go.Scatter(
            x=weekly_df_fahrrad['week'], 
            y=weekly_df_fahrrad['Wert'],
            mode='lines',  # 'lines' mode for line chart
            name='Mean Wert Fahrräder',
            line=dict(color='red') 
        ))

        # Update layout with labels and title
        fig.update_layout(
            title='Wöchentlich Aggregated Values',
            xaxis_title='Week',
            yaxis_title='Mean Wert',
            template='plotly_white'  # Optional, clean background
        )

        # Display the Plotly plot in Streamlit
        st.plotly_chart(fig)
        print('hi')
        print(df_pkws.head())  # Check the first few rows of the PKW dataframe
        
        # Create the pivot table
        pivot = df_pkws.pivot_table(values='q_pkw_mq_hr', index=df_pkws['Date'].dt.weekday, columns='Time', aggfunc='mean')
        pivot = np.floor(pivot).astype(int)
        print(pivot)
        
        # Create the heatmap
        fig = px.imshow(
            pivot.values,
            text_auto=True,
            labels=dict(x="Hour of Day", y="Day of Week", color="Average Users"),
            x=pivot.columns,
            y=pivot.index,
            color_continuous_scale="RdBu"
        )    
    
        fig.update_layout(
            autosize=True,  # Allow Plotly to resize automatically
            margin=dict(l=20, r=20, t=50, b=50),  # Minimize external margins
            width=1200,  # Define the initial width
            height=800,  # Define the initial height
            yaxis=dict(constrain='range' , range=[0,6]),  # Ensure square cells
            coloraxis_colorbar=dict(
                lenmode="fraction",  # Fraction of the figure height
                len=0.5,             # Reduce color bar size to 50% of height
            ),
            showlegend=False,  # Remove legend to avoid cluttering space
            dragmode='zoom',  # Enable zoom functionality
            xaxis=dict(constrain='range')  # Constrain axis range when zoomed

        )
        

    # Update text style (bold)
        fig.update_traces(textfont=dict(weight="bold"))


    # Display the plot in Streamlit with container width enabled
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("No data loaded. Please load the data first.")