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
#Only for testing
dataf = pd.read_csv(r'/Users/anupam/Downloads/titanic.csv')

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
        dd = pd.DataFrame(np.genfromtxt(dataf))
        print(dd)
        return redirect(url_for("datatypes"))
    return render_template("upload.html")

@app.route('/datatypes', methods=["GET","POST"])
def datatypes():
    global dataf

    column_names = dataf.columns.astype('str').tolist()
    data_types = dataf.dtypes.astype('str').tolist()
    datatypes = pd.DataFrame({'column':column_names,'datatype': data_types})
    datatypes['datatype'].replace({'object':'string'}, inplace=True)
    datadict = dftolist(datatypes)

    # print(datadict)
    if request.method == "POST":
        data_types = []
        data_types = request.form.getlist("datatype_from_form")
        print(data_types)
    
        for var, input_type in zip(column_names, data_types):
            if input_type=='str':
                dataf[var] = dataf[var].astype(input_type)
            else:
                # somehow detect very weird values like 'two' in a column int values
                dataf[var].replace({'':np.nan}, inplace=True)
                dataf[var] = dataf[var].astype(input_type)
        return redirect(url_for('preprocessing'))
    print(dataf.head())

    return render_template('datatypes.html', data=datadict)


if __name__ == "__main__":
    
    app.run(debug=True, port = 5000)