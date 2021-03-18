import numpy as np
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models.widgets import Slider
from bokeh.models import ColumnDataSource,Range1d
from bokeh.layouts import row,column,layout

def Constitutive_law(Q,A,n,SigmaP,SigmaR,Temp,Rate):    
    # Constants 
    R = 8.31
    
    Temp = Temp + 273 # convert to Kelvin
    z = Rate*np.exp(Q/(R*Temp))
    yield_stress = 1e6*(SigmaR*np.arcsinh((z/A)**(1.0/n)) + SigmaP)
    return yield_stress

# Variables
Q = 1.56e5
A = 7.00e8
n = 5.0
SigmaP = 3.19
SigmaR = 17.39

# Load in the experimental data
corrected_exp_data = np.load('data/corrected_exp_data.npy')

# Produce the plot
rates = [0.1,1,10] 
temp_range = np.arange(400,610,10)
fig=figure() #create a figure
curdoc().theme = 'light_minimal' # figure theme
colours = ['Red','Green','Blue']
count = 0

## Plotting experimental data
for rate in rates:
    # Experiment
    exp_data = corrected_exp_data[abs(corrected_exp_data[:,3]-rate)<10**(-6)]
    fig.circle(exp_data[:,2],np.log10(exp_data[:,0]),color=colours[count],legend_label=str(rate)+'s-1')
    count = count + 1

## Plotting Sellars-Tegart for the 3 rates
SellarsTegart_01 = np.zeros(len(temp_range))
SellarsTegart_1 = np.zeros(len(temp_range))
SellarsTegart_10 = np.zeros(len(temp_range))

for i in range(len(temp_range)):
    SellarsTegart_01[i] = np.log10(Constitutive_law(Q,A,n,SigmaP,SigmaR,temp_range[i],0.1)*10**(-6)) 
    SellarsTegart_1[i]  = np.log10(Constitutive_law(Q,A,n,SigmaP,SigmaR,temp_range[i],1  )*10**(-6)) 
    SellarsTegart_10[i] = np.log10(Constitutive_law(Q,A,n,SigmaP,SigmaR,temp_range[i],10 )*10**(-6)) 
    
source_01=ColumnDataSource(dict(x=temp_range, y=SellarsTegart_01))
source_1=ColumnDataSource(dict(x=temp_range, y=SellarsTegart_1))
source_10=ColumnDataSource(dict(x=temp_range, y=SellarsTegart_10))

# Baseline
fig.line(temp_range, SellarsTegart_01,color='Red',line_width=2,alpha=0.2)
fig.line(temp_range, SellarsTegart_1,color='Green',line_width=2,alpha=0.2)
fig.line(temp_range, SellarsTegart_10,color='Blue',line_width=2,alpha=0.2)

# Updated
fig.line('x','y',source=source_01,color='Red',line_width=2)
fig.line('x','y',source=source_1,color='Green',line_width=2)
fig.line('x','y',source=source_10,color='Blue',line_width=2)
    
## Set plot aesthetics
fig.xaxis[0].axis_label = 'T / Degrees C'
fig.yaxis[0].axis_label = 'log(Sigma / MPa)'
fig.x_range=Range1d(400, 600)
fig.y_range=Range1d(0.8, 2)

#create a sliders for the variables

def callback(attrname, old, new):
    
    SigmaP_new = sliderSigmaP.value
    SigmaR_new = sliderSigmaR.value
    Q_new = sliderQ.value
    A_new = sliderA.value
    n_new = slidern.value
    
    for rate in rates:
        SellarsTegart_01 = np.zeros(len(temp_range))
        SellarsTegart_1  = np.zeros(len(temp_range))
        SellarsTegart_10 = np.zeros(len(temp_range))
        for i in range(len(temp_range)):
            SellarsTegart_01[i] = np.log10(Constitutive_law(Q_new,A_new,n_new
                                                            ,SigmaP_new,SigmaR_new,temp_range[i],0.1)*10**(-6))
            SellarsTegart_1[i]  = np.log10(Constitutive_law(Q_new,A_new,n_new
                                                            ,SigmaP_new,SigmaR_new,temp_range[i],1  )*10**(-6))
            SellarsTegart_10[i] = np.log10(Constitutive_law(Q_new,A_new,n_new
                                                            ,SigmaP_new,SigmaR_new,temp_range[i],10)*10**(-6))
    source_01.data = dict(x=temp_range, y=SellarsTegart_01)
    source_1.data  = dict(x=temp_range, y=SellarsTegart_1) 
    source_10.data = dict(x=temp_range, y=SellarsTegart_10) 

sliderSigmaP = Slider(title="SigmaP", value=SigmaP, start=0.0, end=20.0,step=0.1)
sliderSigmaR = Slider(title="SigmaR", value=SigmaR, start=0.0, end=20.0,step=0.1)
sliderQ = Slider(title="Q", value=Q, start=1e5, end=2e5,step=1e4)
sliderA = Slider(title="A", value=A, start=6.00e8, end=8.00e8,step=1.00e7)
slidern = Slider(title="n", value=n, start=4, end=6,step=0.1)

sliderSigmaP.on_change('value', callback)
sliderSigmaR.on_change('value', callback)
sliderQ.on_change('value', callback)
sliderA.on_change('value', callback)
slidern.on_change('value', callback)

sliders = column(sliderSigmaP,sliderSigmaR,sliderQ,sliderA,slidern)
plot_layout = layout([[fig,sliders]])
curdoc().add_root(plot_layout)#serve it via "bokeh serve slider.py --show --allow-websocket-origin=*"