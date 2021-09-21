import streamlit as st
import pandas as pd
import numpy as np

from scipy.interpolate import CubicSpline
from scipy.stats import norm
import random
import math

import altair as alt

import matplotlib.pyplot as plt
import seaborn as sns

from streamlit_metrics import metric, metric_row
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder

from PIL import Image

st.set_page_config(layout="wide")   


def main():
    pages = {
        "Home": page_home,
        "Model": page_model,
    }

    if "page" not in st.session_state:
        st.session_state.update({
            # Default page
            "page": "Home",

            # Radio, selectbox and multiselect options
            "options": ["Hello", "Everyone", "Happy", "Streamlit-ing"],

            # Default widget values
            "text": "",
            "slider": 0,
            "checkbox": False,
            "radio": "Hello",
            "selectbox": "Hello",
            "multiselect": ["Hello", "Everyone"],
        })

    with st.sidebar:
        page = st.radio("Go to", tuple(pages.keys()))

    pages[page]()


def page_home():

    st.title("Mejora de Productividad Molienda - Flotación")
    st.write(f"""
    # Explicación
    ## Detalle
    
    """)


def page_model():

    col11, col12, col13 = st.beta_columns((1,10,1))

    with col12:
        st.title("Grinding and flotation optimization")
    
    col21, col22, col23 = st.beta_columns((1,1,1))
    with col22:
        average_p80 =st.number_input("Average P80",min_value=35,max_value=300,value=200)
        std_p80 =st.number_input("Standard Deviation P80",min_value=1,value=15)
        simul_number =st.number_input("Number of Simulations",min_value=1,value=1000,)
        node_number =int(st.selectbox("Number of Nodes",
                ("3", "4", "5","6","7","8")))

    st.write('')
    st.write('')



    node_max=node_number-1
    middle_node_f=math.floor(node_max/2)
    middle_node_c=math.ceil(node_max/2)
    for i in range(node_number):
        j=i+1
        if i<middle_node_f:
            globals()['val_rec_%s' % j]=round(85*(1-(middle_node_f-i)/node_max))
        elif (i==middle_node_f or i==middle_node_c):
            globals()['val_rec_%s' % j]=85
        else:
            globals()['val_rec_%s' % j]=round(85*(1+(middle_node_f-i)/node_max))


    for i in range(node_number):
        j=i+1
        if i<middle_node_c:
            globals()['val_p80_%s' % j]=round(120*(1-(node_max-j)/node_max))
        elif (i==middle_node_f):
            globals()['val_p80_%s' % j]=120
        else:
            globals()['val_p80_%s' % j]=round(120*(0.8*(j)/middle_node_c))


    col31, col32, col33 = st.beta_columns((4,1,4))
    with col31:
        st.subheader('Gráfico de Recuperación versus P80')
    #generamos 3 columnas
    with col33:
        st.subheader('Tabla de Recuperación versus P80')
    #generamos 3 columnas
    col41, col42, col43, col44 = st.beta_columns((3,1,1,1))

    with col43:
        i=0
        st.write('')
        #with st.form('Form1'):
        for i in range(node_number):
            j=i+1
            globals()['p80%s' % j] =st.number_input(f"P80 {j}",max_value=300,value=globals()['val_p80_%s' % j])
        
            #submitted1 = st.form_submit_button('Submit 1')

    with col44:
        
        st.write('')
        i=0
        for i in range(node_number):
            j=i+1
            globals()['rec%s' % j]  =st.number_input(f"Recovery {j}",min_value=0,max_value=100,value=globals()['val_rec_%s' % j])

    data=[]
    for i in range(node_number):
        j=i+1
        data.append([globals()['p80%s' % j],globals()['rec%s' % j ]])

    df_test = pd.DataFrame(data,columns=("p80","Recovery"))
    x=df_test["p80"]
    y=df_test["Recovery"]    

    p80_min=df_test['p80'].min()
    p80_max=df_test['p80'].max()

    max_graph=round(p80_max*1.1)
    min_graph=round(p80_min*0.8)

    f = CubicSpline(x, y, bc_type='natural')
    x_new = np.linspace(0, max_graph, 100)
    y_new = f(x_new)

    prob=random.random()
    norm.ppf(prob,loc=average_p80,scale=std_p80)
    df_rand= pd.DataFrame(np.random.random(size=(simul_number, 1)), columns=['random'])
    df_rand['Simulated_p80']=norm.ppf(df_rand['random'],loc=average_p80,scale=std_p80)

    def check(row):
        if row['Simulated_p80']<35: 
            val=np.nan
        elif row['Simulated_p80']>300: 
            val=np.nan
        else: 
            val=row['Simulated_p80']
        return val


    df_rand['Simulated_p80_check']=df_rand.apply(check, axis=1) 
    df_rand["recovery"]=df_rand['Simulated_p80_check'].apply(f)




    simul_recovery=df_rand[df_rand["recovery"]>0]["recovery"].mean()
    simul_recovery=round(simul_recovery,2)


    with col41:
        st.subheader('')
        color1= "#002A54"
        #'midnightblue'
        color2="#C94F7E"
        #'purple'
        plt.rcParams.update({'font.size': 16})
        fig1, ax = plt.subplots(figsize=(12,8))
        ax2=ax.twinx()
        plt.grid(True, axis='y',linewidth=0.2, color='gray', linestyle='-')
        ax.fill_between(x_new, y_new,alpha=0.1,color=color1,linewidth=2)
        ax.plot(x_new, y_new,linewidth =2, color=color1, alpha=.8)
        ax.plot(x, y, 'o', color=color1)
        ax.set_ylabel("Recovery", color = color1)
        ax.set_xlabel("P80")
        #plt.axhline(y = thr_mean, color = 'r', linestyle = '--',linewidth =0.4)
        #fig1.text(0.7,0.4,'Average: '+str(round(thr_mean)),color='red',size=4)
        plt.ylabel("", fontsize=16)
        plt.xlabel("", fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=16,width=0.2)
        ax.spines['top'].set_linewidth('0.3') 
        ax.spines['right'].set_linewidth('0.3') 
        ax.spines['bottom'].set_linewidth('0.3') 
        ax.spines['left'].set_linewidth('0.3') 
        ax.set_ylim([0,100])
        ax2=sns.histplot(df_rand,x='Simulated_p80_check', bins=20, color=color2,)
        ax2.set_ylabel("Count", color = color2)
        plt.title('Curva Recuperación versus P80',fontsize=22)
        st.pyplot(fig1)

        metric("Simulated Recovery", simul_recovery,)

if __name__ == "__main__":
    main()
