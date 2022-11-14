import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import serial
import streamlit as st
import streamlit_tags as tags
import time as t
from datetime import datetime
import altair as alt
import win32api


st.set_page_config(layout='wide')
st.markdown("""
<style>
.css-18ni7ap.e8zbici2
{
    visibility:hidden;
}
.css-qri22k.egzxvld0
{
    visibility:hidden;
}
.css-9s5bis.edgvbvh3
{
    visibility:hidden;
}
.block-container.css-18e3th9.egzxvld2
{
    padding: 1rem 1rem 1rem 1rem;
}
.css-10trblm.e16nr0p30
{
    text-align:center;
    font-family: Arial;
}
.css-hxt7ib.e1fqkh3o4
{
    padding: 0.5rem 1rem 0rem 1rem;
}
.css-81oif8.effi0qh3
{
    font-size:16px;
}
.css-1p46ort.effi0qh3 {
    font-size: 1px;
    color: rgb(49, 51, 63);
    display: flex;
    visibility: hidden;
    margin-bottom: 0rem;
    height: auto;
    min-height: 0rem;
    vertical-align: middle;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
}
.css-k8kh4s {
    font-size: 1px;
    color: rgba(49, 51, 63, 0.4);
    display: flex;
    visibility: hidden;
    margin-bottom: 0rem;
    height: auto;
    min-height: 0rem;
    vertical-align: middle;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)


if 'arduino' in st.session_state:
    st.session_state.arduino.close()


def cb_live_active():
    st.session_state.cb_live = True
    st.session_state.cb_sig1 = False
    st.session_state.cb_sig2 = False


def cb_sig1_active():
    st.session_state.cb_live = False
    st.session_state.cb_sig1 = True
    st.session_state.cb_sig2 = False


def cb_sig2_active():
    st.session_state.cb_live = False
    st.session_state.cb_sig1 = False
    st.session_state.cb_sig2 = True


def get_x_chart (magnitude ,fig =None):
            meanOfMagnitude=np.mean(magnitude)
            meanOfR=0
            i=1
            length =len(magnitude)-len(magnitude)%20
            for index in range(0,length-20,20):
                max =np.max(magnitude[index:index+21])
                min =np.min(magnitude[index:index+21])
                meanOfR+=(max-min)
                i+=1
            numberOfR=int(len(magnitude)/20)
            meanOfR=meanOfR/numberOfR
            if fig is  not None:
                fig.add_hline(y=meanOfMagnitude+0.18*meanOfR, line_width=3, line_dash="dashdot", line_color="green")
                fig.add_hline(y=meanOfMagnitude-0.18*meanOfR, line_width=3, line_dash='dashdot', line_color='red')
                fig.add_hline((meanOfMagnitude), line_color='yellow',line_width=3,line_dash='solid')
            ucl=meanOfMagnitude+0.18*meanOfR
            lcl=meanOfMagnitude-0.18*meanOfR
            cl=meanOfMagnitude
            return ucl,lcl,cl,meanOfR

def get_r_chart(meanOfR,fig=None):
    ucl =1.59*meanOfR
    lcl=0.41*meanOfR
    cl =meanOfR
    if fig is not None:
        fig.add_hline(y=meanOfR+0.18*meanOfR, line_width=3, line_dash="dashdot", line_color="green")
        fig.add_hline(y=meanOfR-0.18*meanOfR, line_width=3, line_dash='dashdot', line_color='red')
        fig.add_hline((meanOfR), line_color='yellow')
    return ucl ,lcl,cl 


with st.container():
    b1, b2, b3 = st.columns(3)
    cb_live = b1.checkbox("Live Signal", key='cb_live',
                          on_change=cb_live_active)
    cb_sig1 = b2.checkbox("Signal 1", key='cb_sig1',
                          on_change=cb_sig1_active)
    cb_sig2 = b3.checkbox("Signal 2", key='cb_sig2', on_change=cb_sig2_active)


    right_up_col, left_up_col = st.columns([3, 1])
    uploaded_csv = st.sidebar.file_uploader("Upload your CSV file", type={"csv", "txt", "csv.xls"},
                                             label_visibility='collapsed', key="file")

   
    if uploaded_csv is not None:
        uploaded_df = pd.read_csv(uploaded_csv)
        csv_data = uploaded_df.to_numpy()
        time = csv_data[:, 0]
        magnitude = csv_data[:, 1]
        if cb_sig1:
            chart = st.line_chart(
                np.zeros(shape=(1, 1)), height=500, width=1200, use_container_width=False)
            df=pd.DataFrame({'time':time,'value':magnitude},columns=['time','value'])
            
            fig_sig1 = px.line(x=time ,y=magnitude,labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'},height=500,title='X_chart')
            uclX,lclX,clX,meanOfR=get_x_chart(magnitude,fig=fig_sig1)
            
            col1,col2=st.columns(2)
            
            col1.plotly_chart(fig_sig1,use_container_width=True,label ='X-Chart')
            
            fig1_r_chart= px.line(x=time ,y=magnitude,labels={'x': 'Time(s)', 'y': 'Amplitude(mV)'},height=500,title='R_chart')
            ucl,lcl,cl=get_r_chart(meanOfR,fig=fig1_r_chart)
            col2.plotly_chart(fig1_r_chart)
            beebMode=st.sidebar.radio('Beeb with :',('no Beeb','X-Chart','R-Chart'))
            i = 0
            for index in range(0, len(magnitude)-10, 10):
                chart.add_rows(magnitude[index:index+10])
                if beebMode=='X-Chart' and (magnitude[index]>uclX or magnitude[index<lclX]):
                    win32api.Beep(700,60)
                elif beebMode=='R-Chart' and(magnitude[index]>ucl or magnitude[index]<lcl) :
                    win32api.Beep(700,60)
                else:
                    t.sleep(0.05)
                i += 1





        if cb_sig2:

            fig_sig2 = px.line(uploaded_df, x=time,
                               y=magnitude, title="Signal2")
            chart = st.line_chart(
                np.zeros(shape=(1, 1)), height=500, width=1200, use_container_width=False)
            # st.line_chart(fig_sig2,height=500)
            i = 0
            for index in range(0, len(magnitude), 10):
                chart.add_rows(magnitude[i*10:10*(i+1)])
                t.sleep(0.05)
                i += 1



        if cb_live:
            
            arduino=serial.Serial(port='COM16', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=8)
                                    # bytesize=serial.EIGHTBITS)  # Change the COM port to whichever port your arduino is in
            st.session_state.arduino=arduino

            gauge_placeholder = st.empty()
            chart_placeholder = st.empty()

            def temp_gauge(temp, previous_temp, gauge_placeholder):
                fig = go.Figure(go.Indicator(
                    domain={'x': [0, 1], 'y': [0, 1]},
                    value=temp,
                    mode="gauge+number+delta",
                    title={'text': "Temperature (�C)"},
                    delta={'reference': previous_temp},
                    gauge={'axis': {'range': [0, 40]}}))

                gauge_placeholder.write(fig)

            def temp_chart(df, chart_placeholder):
                fig = px.line(df, x="Time", y="Temperature (�C)",
                              title='Temperature vs. time')
                chart_placeholder.write(fig)

            if arduino.isOpen() == False:
                arduino.open()

            i = 0
            previous_temp = 0
            temp_record = pd.DataFrame(
                data=[], columns=['Time', 'Temperature (�C)'])

            while i < 50000000:  # Change number of iterations to as many as you need
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                try :
                    temp =float(arduino.readline().decode().strip('\r\n'))
                except:
                    temp=0
                    
                temp_record.loc[i, 'Time'] = current_time
                temp_record.loc[i, 'Temperature (�C)'] = temp

                temp_gauge(temp, previous_temp, gauge_placeholder)
                temp_chart(temp_record, chart_placeholder)
                
                i += 1
                previous_temp = temp
                # t.sleep(0.1)

            temp_record.to_csv('temperature_record.csv', index=False)
            



