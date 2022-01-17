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

def impute_data(nulls_n):

    global dataf

    for col, imp_typ in zip(nulls_n.column, nulls_n.imp_type):
        if imp_typ == 'row_removal':
            dataf = dataf[dataf[col].notnull()]
        
        print(dataf.loc[dataf.loc[dataf["Age"].isnull(), "Age"].index.tolist(), "Age"])
        if imp_typ == 'mean':
            dataf.loc[dataf[col].isnull(), col] = dataf[col].mean()
        print(dataf.loc[dataf.loc[dataf["Age"].isnull(), "Age"].index.tolist(), "Age"])

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
                dataf[var].replace({'':np.nan}, inplace=True) 
                dataf[var] = dataf[var].astype(input_type)
        return redirect(url_for('preprocessing'))
    print(dataf.head())

    return render_template('datatypes.html', data=datadict)

@app.route("/preprocessing", methods=["GET","POST"])
def preprocessing():
    print(dataf.dtypes)
    return render_template("preprocessing.html")

@app.route("/impute", methods=["GET","POST"])
def impute():
    global dataf

    """ 
    More work needs to be done here to better identify null data fields
    
    """

    dataf.replace({'?':np.nan, 'null':np.nan, 'Null':np.nan, 'NULL':np.nan, '':np.nan}, inplace=True)
    nulls = dataf.isnull().sum().to_frame()
    nulls_n = nulls[nulls[0]>0]
    nulls_n.columns=['null_count']
    
    nulls_n.reset_index(inplace=True)
    print(nulls_n)

    nulls_n.rename( columns = {0:"column"}, inplace=True)
    null_count_frame = dftolist(nulls_n)

    if request.method == "POST":
        imputation_type = request.form.getlist("imputetype")
        nulls_n['imp_type'] = pd.Series(imputation_type)
        print(nulls_n)

        impute_data(nulls_n[['column','imp_type']])
        return redirect(url_for("preprocessing"))
    return render_template("impute.html", data = null_count_frame)

@app.route("/standardize", methods=["GET","POST"])
def standardize():
    return render_template("standardize.html")

@app.route("/encoding", methods=["GET","POST"])
def encoding():
    return render_template("encoding.html")

@app.route("/binning", methods=["GET","POST"])
def binning():
    return render_template("binning.html")




if __name__ == "__main__":
    
    app.run(debug=True, port = 5000)