import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

def app():
    month = None
    year = None
    if 'df_pkws' in st.session_state and 'df_Fahrräder' in st.session_state :
        df_pkws = st.session_state.df_pkws
        df_Fahrräder = st.session_state.df_Fahrräder
        df_pkws['Date'] = pd.to_datetime(df_pkws['Date'], format='%d.%m.%Y')
        df_Fahrräder['Date'] = pd.to_datetime(df_Fahrräder['Date'], format='%d.%m.%Y')
        
        if 'year' in st.session_state and st.session_state.year is not None:
            year = st.session_state.year
            df_pkws = df_pkws[df_pkws['Date'].dt.year == year]
            df_Fahrräder = df_Fahrräder[df_Fahrräder['Date'].dt.year == year]
            st.session_state.enable_month = True 
            
        else:
            st.session_state.enable_month = False 
            
        if 'month' in st.session_state and st.session_state.month is not None:
            month = st.session_state.month
            df_pkws = df_pkws[df_pkws['Date'].dt.month == month]
            df_Fahrräder = df_Fahrräder[df_Fahrräder['Date'].dt.month == month]

        # Wenn keine Optionen ausgewählt wurden, bleiben die originalen DataFrames
        #if 'year' not in st.session_state or st.session_state.year is None or 'month' not in st.session_state or st.session_state.month is None:
        #    df_pkws = st.session_state.df_pkws
        #    df_Fahrräder = st.session_state.df_Fahrräder

        
        with st.expander("Data korrelation"):
            st.header("Data korrelation")
            numerical_columns = ['temperature_2m (°C)', 'relative_humidity_2m (%)', 'rain (mm)', 'snowfall (cm)', 'cloud_cover (%)']

            # Calculate correlation matrix
            corr_matrix_pkws = df_pkws[numerical_columns+['Anzahl']].corr()
            corr_matrix_fahrräder = df_Fahrräder[numerical_columns+['Anzahl']].corr()
            
            col1, col2 = st.columns(2)
            with col1:
            #plt.figure(figsize=(10, 6))
                # Plot the heatmap
                sns.heatmap(corr_matrix_fahrräder, annot=True, cmap='coolwarm', fmt='.2f' ,vmin=-1, vmax=1)
                plt.title('Correlation Heatmap Fahrräders')
                st.pyplot(plt)  # Display the plot
                plt.clf()
                
            with col2:
                # Plot the heatmap
                sns.heatmap(corr_matrix_pkws, annot=True,  fmt='.2f', vmin=-1, vmax=1)
                plt.title('Correlation Heatmap PKWs')
                st.pyplot(plt)  # Display the plot
                plt.clf()
            
        with st.expander("Quartal Graph"):
              
            st.header("PKWs vs Fahrräder Nutzung im Laufe der Zeit (Quartalsweise)")
            df_pkws['year'] = df_pkws['Date'].dt.year
            df_pkws['quarter'] = df_pkws['Date'].dt.quarter

            df_Fahrräder['year'] = df_Fahrräder['Date'].dt.year
            df_Fahrräder['quarter'] = df_Fahrräder['Date'].dt.quarter

            # Group by year and quarter for both datasets and round down the mean for PKWs
            quarterly_traffic_pkws = (
                df_pkws.groupby(['year', 'quarter'])['Anzahl']
                .mean()
                .apply(np.floor)  # Apply floor to round down the mean value
                .reset_index()
            )

            # Group for Fahrräder
            quarterly_traffic_fahrrad = (
                df_Fahrräder.groupby(['year', 'quarter'])['Anzahl']
                .mean()
                .apply(np.floor)
                .reset_index()
            )

            # Combine year and quarter into a single column for x-axis labels
            quarterly_traffic_pkws['year_quarter'] = (
                quarterly_traffic_pkws['year'].astype(str) + '-Q' + quarterly_traffic_pkws['quarter'].astype(str)
            )

            quarterly_traffic_fahrrad['year_quarter'] = (
                quarterly_traffic_fahrrad['year'].astype(str) + '-Q' + quarterly_traffic_fahrrad['quarter'].astype(str)
            )

            fig_pkws = px.line(
                quarterly_traffic_pkws,
                x='year_quarter',
                y='Anzahl',
                #title='Quarterly Traffic Volume: PKWs vs Fahrräder',
                labels={'year_quarter': 'Year-Quarter'},
                markers=True,
                line_shape='linear',
            )
            
            # Update the line color and name for PKWs
            fig_pkws.update_traces(
                line=dict(color='blue'),  # Set the color for PKWs line
                name='PKWs',  # Set the name for the PKWs line in the legend
                hovertemplate="<b>Quarter-Year:</b> %{x}<br><b>PKWs:</b> %{y}<extra></extra>"  # Custom hover info
            )

            # Plot the second line (Fahrräder) using px.line
            fig_fahrrad = px.line(
                quarterly_traffic_fahrrad,
                x='year_quarter',
                y='Anzahl',
                markers=True,
                line_shape='linear',
            )
                        # Update the line color and name for Fahrräder
            fig_fahrrad.update_traces(
                line=dict(color='red'),  # Set the color for Fahrräder line
                name='Fahrräder',  # Set the name for the Fahrräder line in the legend
                hovertemplate="<br><b>Fahrräder:</b> %{y}<extra></extra>"
            )

            # Combine the two figures into one (by adding traces from the second plot to the first)
            for trace in fig_fahrrad.data:
                fig_pkws.add_trace(trace)

            # Update the layout for the combined figure
            fig_pkws.update_layout(
                xaxis=dict(title='Year-Quarter', tickangle=45),
                yaxis=dict(title='Traffic Volume'),
                template='plotly_white',
                hovermode="x unified",  # Tooltip shows values for the current x-axis point
                legend_title="Legend",  # Title for the legend
                showlegend=True,  # Ensure the legend is visible
                legend=dict(
                x=1,  # Position the legend at the top-right corner (1 is fully right)
                y=1,  # Position it at the top (1 is fully top)
                traceorder="normal",  # Ensure the traces are in normal order in the legend
                font=dict(
                    family="Arial",  # Font family
                    size=12,         # Font size
                    color="black"    # Font color
                ),
                bgcolor="white",  # Background color for the legend
                bordercolor="Black",  # Border color
                borderwidth=2      # Border width
                )
            )

            # Show the plot in Streamlit
            st.plotly_chart(fig_pkws, use_container_width=True)
            
        with st.expander("Wöchentlich Graph"):    
                
            st.header("PKWs vs Fahrräder Nutzung im Laufe der Zeit (Wöchentlich)")
            
            # Ensure 'Date' columns are in datetime format
            #df_pkws['Date'] = pd.to_datetime(df_pkws['Date'])
            #df_Fahrräder['Date'] = pd.to_datetime(df_Fahrräder['Date'])
            if month == 12:
                max_week = df_pkws['Date'].dt.isocalendar().week.max()
                # Filtere nur die letzten 5 Kalenderwochen
                last_5_weeks = [max_week - i for i in range(5)]
                df_pkws = df_pkws[df_pkws['Date'].dt.isocalendar().week.isin(last_5_weeks)]
                df_Fahrräder = df_Fahrräder[df_Fahrräder['Date'].dt.isocalendar().week.isin(last_5_weeks)]
            # Extract the week number
            else:
                df_pkws['week'] = df_pkws['Date'].dt.isocalendar().week
                df_Fahrräder['week'] = df_Fahrräder['Date'].dt.isocalendar().week

            # Aggregate the 'Anzahl' column by week for both datasets
            weekly_df_pkw = df_pkws.groupby('week').agg({'Anzahl': 'mean'}).reset_index()
            weekly_df_pkw['Anzahl'] = np.floor(weekly_df_pkw['Anzahl'])

            weekly_df_fahrrad = df_Fahrräder.groupby('week').agg({'Anzahl': 'mean'}).reset_index()
            weekly_df_fahrrad['Anzahl'] = np.floor(weekly_df_fahrrad['Anzahl'])
            
            # Create a Plotly figure
            fig = go.Figure()

            # Add PKWs trace
            fig.add_trace(go.Scatter(
                x=weekly_df_pkw['week'],
                y=weekly_df_pkw['Anzahl'],
                mode='lines',
                name='Mean Wert PKW',
                line=dict(color='blue')
            ))

            # Add Fahrräder trace
            fig.add_trace(go.Scatter(
                x=weekly_df_fahrrad['week'],
                y=weekly_df_fahrrad['Anzahl'],
                mode='lines',
                name='Mean Wert Fahrräder',
                line=dict(color='red')
            ))
            
            # Update the layout of the figure
            fig.update_layout(
                #title='Wöchentlich Aggregated Values',
                xaxis_title='Week',
                yaxis_title='Mean Wert',
                template='plotly_white'  # Optional, clean background
            )

            # Render the plot in Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("Täglich Graph"):
            # Map weekdays to their names
            st.header("PKWs vs Fahrräder Nutzung im Laufe der Zeit (Täglich)")
            weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # Define cell size
            cell_width = 50  # Width of each cell in pixels
            cell_height = 50  # Height of each cell in pixels

            st.subheader("PKWs")
            # Create the pivot table
            pivot = df_pkws.pivot_table(
                values='Anzahl', 
                index=df_pkws['Date'].dt.weekday, 
                columns='Time', 
                aggfunc='mean'
            )
            pivot = np.floor(pivot).astype(int)

            # Calculate figure dimensions
            if(len(pivot.columns)>0 and len(pivot.index)>0):
                fig_width = cell_width * len(pivot.columns)
                fig_height = cell_height * len(pivot.index)
            else:
                fig_width = 100
                fig_height = 100

            # Create the heatmap
            fig = px.imshow(
                pivot.values,
                text_auto=True,
                labels=dict(x="Hour of Day", y="Day of Week", color="Average Users"),
                x=pivot.columns,
                y=weekday_labels[:len(pivot.index)],  # Use only the weekdays present in the index
                color_continuous_scale="RdBu"
            )

            # Customize the layout
            fig.update_layout(
                autosize=False,  # Disable automatic resizing
                width=fig_width,  # Set figure width based on cell size
                height=fig_height,  # Set figure height based on cell size
                margin=dict(l=20, r=20, t=50, b=50),  # Minimize external margins
                yaxis=dict(
                    title="Day of Week",
                    tickvals=list(range(len(pivot.index))),  # Set tick values for each weekday
                    ticktext=weekday_labels[:len(pivot.index)]  # Map tick values to weekday labels
                ),
                xaxis=dict(title="Hour of Day"),
                coloraxis_colorbar=dict(
                    lenmode="fraction",  # Fraction of the figure height
                    len=0.5,             # Reduce color bar size to 50% of height
                )
            )

            # Update text style (bold)
            fig.update_traces(textfont=dict(weight="bold"))

            # Display the plot in Streamlit
            st.plotly_chart(fig, use_container_width=False)

            
            st.subheader("Fahrräders")
            # Create the pivot table
            pivot_F = df_Fahrräder.pivot_table(
                values='Anzahl', 
                index=df_Fahrräder['Date'].dt.weekday, 
                columns='Time', 
                aggfunc='mean'
            )
            pivot_F = np.floor(pivot_F).astype(int)
            
            # Create the heatmap
            fig_F = px.imshow(
                pivot_F.values,
                text_auto=True,
                labels=dict(x="Hour of Day", y="Day of Week", color="Average Users"),
                x=pivot_F.columns,
                y=weekday_labels[:len(pivot_F.index)],  # Use only the weekdays present in the index
                color_continuous_scale="RdBu"
            )

            # Customize the layout
            fig_F.update_layout(
                autosize=False,  # Disable automatic resizing
                width=fig_width,  # Set figure width based on cell size
                height=fig_height,  # Set figure height based on cell size
                margin=dict(l=20, r=20, t=50, b=50),  # Minimize external margins
                yaxis=dict(
                    title="Day of Week",
                    tickvals=list(range(len(pivot_F.index))),  # Set tick values for each weekday
                    ticktext=weekday_labels[:len(pivot_F.index)]  # Map tick values to weekday labels
                ),
                xaxis=dict(title="Hour of Day"),
                coloraxis_colorbar=dict(
                    lenmode="fraction",  # Fraction of the figure height
                    len=0.5,             # Reduce color bar size to 50% of height
                )
            )

            # Update text style (bold)
            fig.update_traces(textfont=dict(weight="bold"))

            # Display the plot in Streamlit
            st.plotly_chart(fig_F, use_container_width=False)
                
    else:
        st.warning("No data loaded. Please load the data first.")
        
        #wenn kein Jahr dann monat auf None 
        # Map inder Mitte