from crypt import methods
from flask import Flask, render_template, url_for, request, redirect
import flask_excel as excel
import pandas as pd
import numpy as np

def dftolist(dataf):

    list_of_dict=[]
    cols = dataf.columns.tolist()

    for i in range(dataf.shape[0]):
        internal_dict={}

        for j, val in enumerate(dataf.iloc[i,:].values):
            internal_dict[cols[j]] = val

        list_of_dict.append(internal_dict) 
    return list_of_dict

dataf=pd.DataFrame([])

app = Flask(__name__)
excel.init_excel(app)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/upload', methods=["GET","POST"])
def upload():
    global dataf
    if request.method=="POST":

        dataf = pd.DataFrame(request.get_array(field_name='file'))
        dataf.columns = dataf.iloc[0,:]
        dataf = dataf.iloc[1:,:]
        return redirect(url_for("datatypes"))
    return render_template("upload.html")

@app.route('/datatypes', methods=["GET","POST"])
def datatypes():
    
    #Only for testing
    # dataf = pd.read_csv(r'/Users/anupam/Documents/csv_file.csv')
    column_names = dataf.columns.astype('str').tolist()
    data_types = dataf.dtypes.astype('str').tolist()
    datatypes = pd.DataFrame({'column':column_names,'datatype': data_types})
    datadict = dftolist(datatypes)

    # print(datadict)
    if request.method == "POST":
        data_types = []
        data_types.append(request.form.getlist("datatype_from_form"))
        data_types = pd.Series(data_types[0]).replace({'object':'str'}).tolist()
        # print(data_types)
    
        for var, input_type in zip(column_names, data_types):
           dataf[var] = dataf[var].astype(input_type)
        
        # print(dataf.head())
        # print(dataf.dtypes)
        
        return redirect(url_for('preprocessing'))

    return render_template('datatypes.html', data=datadict)

@app.route("/preprocessing", methods=["GET","POST"])
def preprocessing():
    return render_template("preprocessing.html")

if __name__ == "__main__":
    
    # excel.init_excel(app)
    app.run(debug=True, port = 5000)