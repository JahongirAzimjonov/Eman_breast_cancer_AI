import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
# from sklearn.linear_model import SGDRegressor, RidgeCV, Ridge
# from sklearn.linear_model import SGDClassifier
from sklearn import linear_model as lm
from sklearn import svm
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from time import time
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import Tcl
import tkinter as tk
import sys
import json
import os
import seaborn as sns
# import statsmodels.formula.api as sm
import statsmodels.regression.linear_model as sm
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold

# Recursive feature elimination with cross-validation
csvm_features_to_select = 1
lsvm_features_to_select = 1
sgdc_features_to_select = 1
logr_features_to_select = 1
ridr_features_to_select = 1
def rfe_with_cv(X,y, plot_path, classifier):
    global csvm_features_to_select
    global lsvm_features_to_select
    global sgdc_features_to_select
    global logr_features_to_select
    global ridr_features_to_select

    feature_names = X.columns
    min_features_to_select = 1  # Minimum number of features to consider
    # clf = lm.LogisticRegression()
    classifiers = [
                   svm.SVC(kernel='linear', random_state=global_random_state_number, max_iter=511),
                   svm.LinearSVC(random_state=global_random_state_number, max_iter=511),
                   lm.LogisticRegression(penalty='l2', random_state=global_random_state_number, max_iter=511),
                   lm.RidgeClassifier(random_state=global_random_state_number, max_iter=511),
                   lm.SGDClassifier(random_state=global_random_state_number, max_iter=511)
                  ]
    clf = ""
    std_dev_error_color='purple'
    mean_test_acc_color='lime'
    if classifier == "c-svm":
        clf = classifiers[0]
        std_dev_error_color='purple'
        mean_test_acc_color='lime'
    elif classifier == "l-svm":
        clf = classifiers[1]
        std_dev_error_color='red'
        mean_test_acc_color='royalblue'
    elif classifier == "logistic":
        clf = classifiers[2]
        std_dev_error_color='magenta'
        mean_test_acc_color='cyan'
    elif classifier == "ridge":
        clf = classifiers[3]
        std_dev_error_color='red'
        mean_test_acc_color='royalblue'
    elif classifier == "sgdc":
        clf = classifiers[4]
        std_dev_error_color='magenta'
        mean_test_acc_color='lime'
    else:
        clf = classifiers[4]
        std_dev_error_color='magenta'
        mean_test_acc_color='lime'
    
    cv = StratifiedKFold(5)

    rfecv = RFECV(
        estimator=clf,
        step=1,
        cv=cv,
        scoring="accuracy",
        min_features_to_select=min_features_to_select,
        n_jobs=2,
    )
    rfecv.fit(X, y)

    selected_features_with_rfecv = feature_names[rfecv.get_support()]
    print(f"\nOptimal number of features: {rfecv.n_features_}\nThe selected features:{selected_features_with_rfecv}\n")
    sfs_df = pd.DataFrame(data=selected_features_with_rfecv, columns=[f"{classifier.upper()}-best-features"])
    sfs_df.to_csv(f"{plot_path}/sfs_with_rfecv_and_{classifier}.csv", index=False)

    n_scores = len(rfecv.cv_results_["mean_test_score"])

    if classifier == "c-svm":
        csvm_features_to_select = rfecv.n_features_
    elif classifier == "l-svm":
        lsvm_features_to_select = rfecv.n_features_
    elif classifier == "logc":
        logr_features_to_select = rfecv.n_features_
    elif classifier == "ridc":
        ridr_features_to_select = rfecv.n_features_
    elif classifier == "sgdc":
        sgdc_features_to_select = rfecv.n_features_

    
    plt.figure(figsize=(27,15), layout="constrained")
    
    plt.xlabel("Number of features selected", fontdict={'fontsize':41, 'fontweight':"bold"})
    plt.ylabel("Mean test accuracy", fontdict={'fontsize':41, 'fontweight':"bold"})
    
    plt.xticks(ha='right', fontsize=23, fontweight="bold")
    plt.xticks(ticks=np.arange(0, len(X.columns)+1, 1), fontsize=17, fontweight="bold", rotation=90)
    
    plt.yticks(fontsize=23, fontweight="bold")

    rfecv_grid_scores = rfecv.cv_results_['mean_test_score']
    print(f"RFECV grid scores: {rfecv_grid_scores}\n")

    # print(f"RFECV ranking: {rfecv.ranking_}\n")

    # worst_score = round(min(rfecv.grid_scores_[np.argmax(rfecv.ranking_ )]),2)
    worst_score = round(min(rfecv_grid_scores), 2)

    # best_score = round(max(rfecv.grid_scores_[np.argmax(rfecv.ranking_ )]),2)
    best_score = round(max(rfecv_grid_scores), 2)
    
    plt.yticks(ticks=np.arange(worst_score-0.11, best_score+0.05, 0.05), fontsize=29, fontweight="bold")    
    plt.ylim(worst_score-0.11, best_score+0.05)
    
    plt.errorbar(
        range(min_features_to_select, n_scores + min_features_to_select),
        rfecv.cv_results_["mean_test_score"],
        yerr=rfecv.cv_results_["std_test_score"],
        ecolor=std_dev_error_color,
        color=mean_test_acc_color,        
        linewidth=4,
        capsize=3, 
        elinewidth=2,
        markeredgewidth=2,
        alpha=0.75
    )

    plt.grid()
    
    # plt.title(f"Recursive Feature Elimination with correlated features.\nOptimal number of features: {rfecv.n_features_}")
    plt.title(f"    Relationship between '{classifier.upper()}' classifier accuracy and number of features. \
              \nThe estimated optimal number of trainable features is {rfecv.n_features_}.\nThe best score is {best_score*100}%.",
              fontdict={'fontsize':41, 'fontweight':"bold"})
    
    # plt.legend(title='Classification Accuracy Scores')
    # plt.gca().legend(('Mean Test Accuracy Score', 'Standart Deviation Error'), fontdict={'fontsize':21, 'fontweight':"bold"})
    plt.legend([f'Mean Test Accuracy Score ({mean_test_acc_color.upper()})\nStandart Deviation Score ({std_dev_error_color.upper()})'], 
               loc='lower right', 
               prop = {'weight':"bold", 'size':37}
               )
    plt.savefig(plot_path + f"{classifier.upper()}-Features_vs_Accuracy.png", dpi = 100)

    plt.show()
    return selected_features_with_rfecv

def feature_selection_via_VarianceThreshold(X, percent):
    feature_names = X.columns
    p = percent 
    formula_p = p * (1 - p)
    # formula_p = 1
    sf_var_thresh = VarianceThreshold(threshold=formula_p)
    sf_var_thresh.fit_transform(X)
    print(sf_var_thresh.get_support())
    print(X[sf_var_thresh.get_feature_names_out(feature_names)].columns)
    return feature_names[sf_var_thresh.get_support()]

def get_file_path(initDirPath):
        file_path = ""
        file_select_window = tk.Tk()
        file_select_window.withdraw()
        # print(tk1)
        # show an "Open" dialog box and return the path to the 	selected file
        filePath = filedialog.askopenfilename(initialdir = initDirPath,
                                            title = "Select file",
                                            filetypes = (
                                                         ("CSV files","*.csv"),
                                                         ("Excel(.xls) files", "*.xls"),
                                                         ("Excel(.xlsx) files", "*.xlsx"),
                                                         ("all files","*.*")
                                                        )
                                             )
        file_select_window.destroy()

        if (filePath!=""):
            file_path = filePath
            return file_path
        else:
            print("Any file has not been selected!")
            return -1

def get_file_name_and_ext(file_path):
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))
    return file_name, file_ext

def bca_wisconsin_format_fit(df):
    df = df.drop(['id'], axis = 1)
    return df

def CBIS_DDSM_format_fit(df):
    return df

def dataset_imbalance_test(target_output, dataset_text, path_to_save_plots, plot_name):
    classes = []
    class_distribution = []

    for colName in target_output:
        if colName not in classes:
            classes.append(colName)
            class_distribution.append(1)
        else:
            classID = classes.index(colName)
            class_distribution[classID] += 1

    print(f"Target Classes:\n{classes} and their distribution:\n{class_distribution}\n")
    print(f"Length of classes: {len(classes)}\nLenth of class distribution:{len(class_distribution)}\n")
    
    plt.figure(figsize=(10,8), layout="constrained")

    # plt.bar(classes, class_distribution, color=('lightgreen', 'lightpink', 'violet', 'pink'))
    col_normal = 'green'
    col_attack = 'deeppink'
    if classes[0] == "B" or classes[0] == "b" or classes[0] == 'Benign' or classes[0] == 'benign':
        classes = ["Benign", "Malignant"]
        plt.bar(classes, class_distribution, color=(col_normal, col_attack), alpha=0.75)
    if classes[0] == "M" or classes[0] == "m" or classes[0] == 'Malignant' or classes[0] == 'malignant':
        classes = ["Malignant", "Benign"]
        plt.bar(classes, class_distribution, color=(col_attack, col_normal), alpha=0.55)
    # giving title to the plot
    plt.title(dataset_text, fontweight="bold", fontsize=15)
    
    for clsDistID in range(len(class_distribution)):
        plt.text(x=classes[clsDistID], y = class_distribution[clsDistID] , \
            s=f"{class_distribution[clsDistID]}", fontdict=dict(fontsize=15, fontweight="bold"))

    # for cdID, cls_dist in enumerate(class_distribution):
    #     plt.text(x=classes[cdID] , y = class_distribution[0] , s=f"{class_distribution[0]}" , fontdict=dict(fontsize=20))
    # plt.text(x=1 , y = class_distribution[1] , s=f"{class_distribution[1]}" , fontdict=dict(fontsize=20))
    
    # giving X and Y labels
    plt.xlabel("Class Labels", fontweight="bold", fontsize=15)
    plt.ylabel("Number of Samples by Class", fontweight="bold", fontsize=15)
    plt.xticks(rotation=30, ha='right', fontsize=15, fontweight="bold")
    plt.yticks(fontsize=13, fontweight="bold")
    # plt.pie(class_distribution)
    plt.savefig(path_to_save_plots + f"cls_imb_{plot_name}.png", dpi=100)
    plt.show()

# Calculating feature importance coefficients
def feature_importance_coefficients(feature_select_model):
    importance = np.abs(feature_select_model.coef_)
    ## If we want to select only 2 features, we will set this threshold slightly above 
    ## the coefficient of third most important feature. It means, we get the first two features
    ## with the greatest values. To activate this, just uncomment the following line:
    # threshold = np.sort(importance)[-3] + 0.01    
    ## If we want to select the features above the average value of the importance coefficients, 
    ## then it will be sufficient to set the threshold an average value of importance array:
    threshold = np.average(importance) 
    return [importance, threshold]

def display_feature_importance_coefficients(importance, feature_names, fs_model_name, path_to_save_plots):
    plt.figure(figsize=(16,10), layout="constrained")

    feature_names = np.array(feature_names)

    y_line = np.average(importance)
    # Number of selected features whose importance coefficient value is greater than average.
    num_sf = np.count_nonzero(importance > y_line)    
    plt.axhline(y_line, 
                color='red', 
                linestyle='dashed', 
                linewidth=3, 
                label=f"{num_sf} features with an Importance Coefficient\nGreater than the Average ({round(y_line,2)}) were Selected."
                        )
    # plt.text(10, y_line, , fontsize=15, va='bottom', ha='center')#, backgroundcolor='w')
    plt.legend(fontsize=21)
    
    plt.bar(height=importance, x=feature_names, color="violet")
    # plt.barh(width=importance, y=feature_names, color="violet")
    plt.xticks(rotation=90, ha='right', fontsize=11, fontweight="bold")
    plt.yticks(fontsize=11, fontweight="bold")
    plt.title(f"Feature Importance Coefficients Calculated via '{fs_model_name}'", fontsize=15, fontweight="bold")
    # giving X and Y labels
    plt.xlabel(f"Features ({len(feature_names)} in total.)", fontsize=15, fontweight="bold")
    plt.ylabel("Feature Importance Coefficients", fontsize=15, fontweight="bold")
    for clsDistID in range(len(importance)):
        plt.text(x=feature_names[clsDistID] , y = importance[clsDistID] , s=f"{round(importance[clsDistID],4)}", 
            fontdict=dict(fontsize=15, ha='center', fontweight="bold"))
    plt.savefig(path_to_save_plots + "feature_importance_coefficients.png", dpi = 100)
    # plt.show()        

# Selecting features, based on the importance coefficient value (Model-based feature selection).
# Features that have an importance coefficient value greater than the average of 
# the importance coefficient values of all features were selected. 
def selecting_features_based_on_importance(X, y, feature_select_model, importance, path_to_save_docs):
    feature_names = X.columns
    # The threshold was set as the average of the importance coefficient values
    threshold = np.average(importance)   
    tic = time()
    sfm = SelectFromModel(estimator = feature_select_model, max_features=number_of_features_to_select).fit(X, y)
    # sfm = SelectFromModel(estimator = feature_select_model, threshold=threshold).fit(X, y)
    toc = time()
    # print(f"Features selected by SelectFromModel: {feature_names[sfm.get_support()]}")
    fs_data = {"Importance Coefficient-based Feature Selection":[f"{1000 * (toc - tic):.3f}"],
               "Time Units":["ms"]}
    fs_df = pd.DataFrame(data=fs_data)
    fs_df.to_excel(path_to_save_docs + "FS_TimeForImportanceCoefficient.xlsx")
    print(f"Importance Coefficient-based Feature Selection Done in {1000 * (toc - tic):.3f}ms")
    selected_feature_names_imco = feature_names[sfm.get_support()]
    if len(selected_feature_names_imco) == 0:
        return feature_names[:number_of_features_to_select] 
    else:
        return selected_feature_names_imco


# The sequential feature selection methods
def forward_sequential_feature_selection(X, y, feature_select_model, number_of_features_to_select, path_to_save_docs):
    feature_names = X.columns
    if len(feature_names) < number_of_features_to_select:
        number_of_features_to_select = len(feature_names) 

    # Selecting features with Sequential Feature Selection
    tic_fwd = time()
    sfs_forward = SequentialFeatureSelector(
        feature_select_model, n_features_to_select=number_of_features_to_select, direction="forward"
    ).fit(X, y)
    toc_fwd = time()
    # print(
    #     "Features selected by forward sequential selection: "
    #     f"{feature_names[sfs_forward.get_support()]}"
    # )
    fs_data = {"Forward Sequential Feature Selection":[f"{1000 * (toc_fwd - tic_fwd):.3f}"],
               "Time Units":["ms"]}
    fs_df = pd.DataFrame(data=fs_data)
    fs_df.to_excel(path_to_save_docs + "FS_TimeForForwardSequential.xlsx")
    print(f"Forward Sequential-based feature selection Done in {1000 * (toc_fwd - tic_fwd):.3f}ms")

    return feature_names[sfs_forward.get_support()]

def backward_sequential_feature_selection(X, y, feature_select_model, number_of_features_to_select, path_to_save_docs):
    feature_names = X.columns
    if len(feature_names) < number_of_features_to_select:
        number_of_features_to_select = len(feature_names) 

    tic_bwd = time()
    sfs_backward = SequentialFeatureSelector(
        feature_select_model, n_features_to_select=number_of_features_to_select, direction="backward"
    ).fit(X, y)
    toc_bwd = time()
    # print(
    #     "Features selected by backward sequential selection: "
    #     f"{feature_names[sfs_backward.get_support()]}"
    # )
    fs_data = {"Backward Sequential Feature Selection":[f"{1000 * (toc_bwd - tic_bwd):.3f}"],
               "Time Units":["ms"]}
    fs_df = pd.DataFrame(data=fs_data)
    fs_df.to_excel(path_to_save_docs + "FS_TimeForBackwardSequential.xlsx")
    print(f"Backward Sequential-based feature selection Done in {1000 * (toc_bwd - tic_bwd):.3f}ms")

    return feature_names[sfs_backward.get_support()]

# Pearson Correlation Coefficient
def pearson_correlation_coefficients(df):  
    corr = df.corr()
    corr = np.round(corr, 2)
    return corr

# Selecting columns based on p-value
def backwardElimination(x, Y, sl, columns):
    numVars = len(x[0])
    for i in range(0, numVars):
        regressor_OLS = sm.OLS(Y, x).fit()
        maxVar = max(regressor_OLS.pvalues).astype(float)
        if maxVar > sl:
            for j in range(0, numVars - i):
                if (regressor_OLS.pvalues[j].astype(float) == maxVar):
                    x = np.delete(x, j, 1)
                    columns = np.delete(columns, j)
    return x, columns   

#Feature selection using Pearson Correlation Coefficient 
def feature_selection_with_pearson_corr_coef(df, target_ouput_name, corr, path_to_save_docs):
    tic_corr = time()
    y = df[target_ouput_name].values
    # Here, we compare the correlation between features and 
    # remove one of two features that have a correlation higher than 0.9
    columns = np.full((corr.shape[0],), True, dtype=bool)
    corr_target = corr[target_ouput_name]
    # np_corr_target = corr_target.values
    # avg_corr = np_corr_target[np_corr_target>0].mean()
    # for col_id in range(0,len(columns)):
    #     if corr_target.loc[corr_target.index[col_id]] < 0.2:
    #         columns[col_id] = False
    for i in range(corr.shape[0]):
        for j in range(i+1, corr.shape[0]):
            if corr.iloc[i,j] > 0.9:
                if columns[j]:
                    columns[j] = False            
    
    selected_columns = df.columns[columns]    
    df = df[selected_columns]
   
    # Selecting columns based on p-value. Next we will be selecting the columns based on how they affect the p-value. 
    # We are going to remove the target_output column, because it is the column we are trying to predict.
    # selected_columns = selected_columns[1:].values # works only if the target output is in the first column of the dataframe 
    if target_ouput_name in df.columns:
        selected_columns = df.drop([target_ouput_name], axis=1).columns # works universally, it means it just drop the target output column
    
    X = df[selected_columns]

    SL = 0.05
    data_modeled, selected_columns = backwardElimination(X.values, y, SL, selected_columns)
    toc_corr = time()
    fs_data = {"Feature Selection via Corr.Coef. with BE":[f"{1000 * (toc_corr - tic_corr):.3f}"],
               "Time Units":["ms"]}
    fs_df = pd.DataFrame(data=fs_data)
    fs_df.to_excel(path_to_save_docs + "FS_TimeForCorr.Coef.BE.xlsx")
    print(f"Feature selection based on the correlation coefficients and p-value Done in {1000 * (toc_corr - tic_corr):.3f}ms")

    # return data_modeled, selected_columns
    return df[selected_columns], selected_columns
    
def display_pearson_correlation_coefficients(corr, path_to_save_plots):
    plt.figure(figsize=(20,12), layout="constrained")
    plt.title("The Correlation Coefficients Heatmap", fontsize=15, fontweight="bold")
    ax = sns.heatmap(corr, annot=True, fmt=".1f")
    # ax.set(xlabel="Feature Correlation Coefficients", ylabel="Feature Correlation Coefficients", )
    # set labels and font size
    ax.set_xlabel("Features Correlation Coefficients", fontsize = 15, fontweight = "bold")
    ax.set_ylabel("Features Correlation Coefficients", fontsize = 15, fontweight = "bold")

    ax.xaxis.tick_top()
    plt.xticks(rotation=90, fontsize=11, fontweight="bold")
    plt.yticks(fontsize=11, fontweight="bold")
    plt.savefig(path_to_save_plots + "Correlation Coefficients.png", dpi = 300)
    # plt.show()

def visualize_selected_feature_distributions(X, y, selected_features, target_name, feature_selection_method_name, fs_model_name, path_to_save_plots):
    X_with_selected_features = X[selected_features]
    X_wsf_cols = X_with_selected_features.columns
    
    number_of_featuresX = len(X_wsf_cols)
    # print(f"number_of_featuresX:{number_of_featuresX}")
    num_of_subplot_rows=2
    num_of_subplot_cols=2
    if number_of_featuresX >= 1 or number_of_featuresX <= 4:
        num_of_subplot_rows = 2
        num_of_subplot_cols = 2
    if number_of_featuresX == 5 or number_of_featuresX == 6:
        num_of_subplot_rows = 2
        num_of_subplot_cols = 3
    if number_of_featuresX >= 7 and number_of_featuresX <= 9:
        num_of_subplot_rows = 3
        num_of_subplot_cols = 3
    if number_of_featuresX >= 10 and number_of_featuresX <= 12:
        num_of_subplot_rows = 3
        num_of_subplot_cols = 4
    if number_of_featuresX >= 13 and number_of_featuresX <= 15:
        num_of_subplot_rows = 3
        num_of_subplot_cols = 5
    if number_of_featuresX > 15 and number_of_featuresX <= 20:
        num_of_subplot_rows = 4
        num_of_subplot_cols = 5
    if number_of_featuresX >= 21 and number_of_featuresX <= 25:
        num_of_subplot_rows = 5
        num_of_subplot_cols = 5
    if number_of_featuresX > 25 and number_of_featuresX <= 30:
        num_of_subplot_rows = 5
        num_of_subplot_cols = 6
    if number_of_featuresX > 30 and number_of_featuresX <= 35:
        num_of_subplot_rows = 5
        num_of_subplot_cols = 7
    if number_of_featuresX > 35 and number_of_featuresX <= 42:
        num_of_subplot_rows = 6
        num_of_subplot_cols = 7
    
    result = pd.DataFrame()
    result[target_name] = y

    fig, axes = plt.subplots(nrows=num_of_subplot_rows, 
                             ncols=num_of_subplot_cols, 
                             constrained_layout=True, 
                             figsize=(25,15))
    colID = 0
    for row in range(num_of_subplot_rows):
        # print(f"row :{row}")
        for col in range(num_of_subplot_cols):
            # print(f"col :{col}")
            if colID < len(X_wsf_cols):
                # print(f"colID:{colID} and len:{len(X_wsf_cols)}")
                sns.distplot(X_with_selected_features[X_wsf_cols[colID]][result[target_name]==0], color='g', label = 'Benign', ax=axes[row,col])
                sns.distplot(X_with_selected_features[X_wsf_cols[colID]][result[target_name]==1], color='deeppink', label = 'Malignant', ax=axes[row,col])
                axes[row,col].legend()
                colID += 1
    fig.suptitle(f"The Features, Selected based on the '{feature_selection_method_name}' with '{fs_model_name}'", fontsize = 15, fontweight="bold")
    fig.tight_layout()
    fig.subplots_adjust(top=0.8)
    plt.savefig(path_to_save_plots + feature_selection_method_name + ".png", dpi = 300)
    # plt.show()

# Test a model with a dataset via its selected features
def test_ml_model_with_selected_features(model, data_modeled, y, selected_features, fs_method_name, fs_model_name, path_to_save_plots, path_to_save_docs):
    plt.figure(figsize=(9,15), layout="constrained")
    global_test_size
    global_random_state_number
    data = pd.DataFrame(data = data_modeled, columns = selected_features)
    # scaler = MinMaxScaler()
    # scaler = StandardScaler()
    # data = pd.DataFrame(scaler.fit_transform(data.values), columns=data.columns, index=data.index)
    
    x_train, x_test, y_train, y_test = train_test_split(data.values, y.values, test_size = global_test_size, random_state=global_random_state_number)

    trainingStartTime = time()
    model.fit(x_train, y_train)
    trainingStopTime = time()
    print(f"Training time for {fs_method_name} Done in {1000 * (trainingStopTime - trainingStartTime):.3f}ms")
    
    testingStartTime = time()
    y_pred = model.predict(x_test)
    testingStopTime = time()
    print(f"Testing time for {fs_method_name} Done in {1000 * (testingStopTime - testingStartTime):.3f}ms")
    print(f"Testing time per record for {fs_method_name} Done in {1000 * (testingStopTime - testingStartTime)/len(y_test):.6f}ms\n")

    # print(classification_report(y_test, y_pred, digits = 6, target_names=["Benign", "Malignant"]))

    classifier_report = classification_report(y_true = y_test, 
                                              y_pred = y_pred, 
                                              digits = 6, 
                                              output_dict = True, 
                                              target_names = ["Benign", "Malignant"])    
    df_classifier = pd.DataFrame(classifier_report).transpose()
    df_classifier = np.round(df_classifier, 4)
    df_classifier.at['accuracy', 'support'] = df_classifier.iloc[3, df_classifier.columns.get_loc('support')]
    df_classifier.at['accuracy', 'precision'] = ""
    df_classifier.at['accuracy', 'recall'] = ""
    df_classifier = df_classifier.astype({"support": int})
    df_classifier = df_classifier.rename(columns = {"precision": "Precision", "recall": "Re-Call", "f1-score":"F1-Score", "support":"Support"}, 
                                         index   = {"accuracy": "Accuracy", "macro avg":"Macro AVG", "weighted avg":"Weighted AVG"})
    
    empty_space_line = pd.DataFrame({"Precision": "-----", "Re-Call": "-----", "F1-Score":"-----", "Support":"-----"}, index=["-----"])
    df_classifier_temp = pd.concat([df_classifier.iloc[:2], empty_space_line, df_classifier.iloc[2:]])#.reset_index(drop=True)
    df_classifier = df_classifier_temp

    train_test_res_df = pd.DataFrame({"Precision": [f"{1000 * (trainingStopTime - trainingStartTime):.3f}",
                                                    f"{1000 * (testingStopTime - testingStartTime):.3f}",
                                                    f"{1000 * (testingStopTime - testingStartTime)/len(y_test):.6f}"],                                                         
                                      "Re-Call": ["-----","-----","-----"], 
                                      "F1-Score":["-----","-----","-----"], 
                                      "Support":["-----", "-----", "-----"]},
                                      index=["Training Time", "Test Time-All Records", "Test Time-Per Record"])
    
    empty_space_line = pd.DataFrame({"Precision": "-----", "Re-Call": "-----", "F1-Score":"-----", "Support":"-----"}, index=["-----"])
    df_classifier = pd.concat([df_classifier.iloc[:6], empty_space_line, train_test_res_df])#.reset_index(drop=True)
    print(f"Cm df:\n{df_classifier}\n")

    df_classifier.to_latex(path_to_save_docs + fs_method_name + ".tex")
    df_classifier.to_excel(path_to_save_docs + fs_method_name + ".xlsx")
    df_classifier.to_csv(path_to_save_docs + fs_method_name + ".csv", index=True)

    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)        
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                            #   display_labels=model.classes_)
                            display_labels=["Benign", "Malignant"])
    disp.plot()  
    
    for labels in disp.text_.ravel():
        labels.set_fontsize(15)
        labels.set_fontweight("bold")     
    
    plt.title(f"{fs_method_name} with\n{fs_model_name}", fontsize = 15, fontweight = "bold")
    
    plt.xlabel(xlabel="Predicted Label", fontsize=15, fontweight="bold")
    plt.ylabel(ylabel="True Label", fontsize=15, fontweight="bold")
    
    plt.xticks(fontsize=15, fontweight="bold")
    plt.yticks(rotation=90, fontsize=15, fontweight="bold")
    
    plt.savefig(f"{path_to_save_plots}{fs_method_name}_{fs_model_name}.png", dpi=100)
    
    # plt.show()
    
    sum = 0
    for i in range(cm.shape[0]):
        sum += cm[i][i]
        
    accuracy = sum/x_test.shape[0]
    # print(f"The accuracy of a model, trained on the selected features: {accuracy}")
    return accuracy

# Building a model without feature selection and comparing the results
# Next, we repeat all the ab# sns.set(font_scale)             ove steps except feature selection, which are:
#     Loading the data, Removing the unwanted columns, Encoding the categorical variable,
#     Splitting the data into train and test set, Fitting the data to the model,
#     Making the predictions and calculating the accuracy
def test_ml_model_with_all_features(model, x_train, y_train, x_test, y_test, fs_method_name, path_to_save_plots, path_to_save_docs):     
    plt.figure(figsize=(9,11), layout="constrained") 
    trainingStartTime = time()
    model.fit(x_train, y_train)
    trainingStopTime = time()
    print(f"Training time for {fs_method_name} Done in {1000 * (trainingStopTime - trainingStartTime):.3f}ms")
    
    testingStartTime = time()
    y_pred = model.predict(x_test)
    testingStopTime = time()
    print(f"Testing time for {fs_method_name} Done in {1000 * (testingStopTime - testingStartTime):.3f}ms")
    print(f"Testing time per record for {fs_method_name} Done in {1000 * (testingStopTime - testingStartTime)/len(y_test):.6f}ms\n")

    # print(classification_report(y_test, y_pred, digits = 6, target_names=["Benign", "Malignant"]))

    classifier_report = classification_report(y_true = y_test, 
                                              y_pred = y_pred, 
                                              digits = 6, 
                                              output_dict = True, 
                                              target_names = ["Benign", "Malignant"])    
    df_classifier = pd.DataFrame(classifier_report).transpose()
    df_classifier = np.round(df_classifier, 4)
    df_classifier.at['accuracy', 'support'] = df_classifier.iloc[3, df_classifier.columns.get_loc('support')]
    df_classifier.at['accuracy', 'precision'] = ""
    df_classifier.at['accuracy', 'recall'] = ""
    df_classifier = df_classifier.astype({"support": int})
    df_classifier = df_classifier.rename(columns = {"precision": "Precision", "recall": "Re-Call", "f1-score":"F1-Score", "support":"Support"}, 
                                         index   = {"accuracy": "Accuracy", "macro avg":"Macro AVG", "weighted avg":"Weighted AVG"})
    
    empty_space_line = pd.DataFrame({"Precision": "-----", "Re-Call": "-----", "F1-Score":"-----", "Support":"-----"}, index=["-----"])
    df_classifier_temp = pd.concat([df_classifier.iloc[:2], empty_space_line, df_classifier.iloc[2:]])#.reset_index(drop=True)
    df_classifier = df_classifier_temp

    train_test_res_df = pd.DataFrame({"Precision": [f"{1000 * (trainingStopTime - trainingStartTime):.3f}",
                                                    f"{1000 * (testingStopTime - testingStartTime):.3f}",
                                                    f"{1000 * (testingStopTime - testingStartTime)/len(y_test):.6f}"],                                                         
                                      "Re-Call": ["-----","-----","-----"], 
                                      "F1-Score":["-----","-----","-----"], 
                                      "Support":["-----", "-----", "-----"]},
                                      index=["Training Time", "Test Time-All Records", "Test Time-Per Record"])
    
    empty_space_line = pd.DataFrame({"Precision": "-----", "Re-Call": "-----", "F1-Score":"-----", "Support":"-----"}, index=["-----"])
    df_classifier = pd.concat([df_classifier.iloc[:6], empty_space_line, train_test_res_df])#.reset_index(drop=True)
    print(f"Cm df:\n{df_classifier}\n")

    df_classifier.to_latex(path_to_save_docs + fs_method_name + ".tex")
    df_classifier.to_excel(path_to_save_docs + fs_method_name + ".xlsx")
    df_classifier.to_csv(path_to_save_docs + fs_method_name + ".csv", index=True)

    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)        
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                            #   display_labels=model.classes_)
                            display_labels=["Benign", "Malignant"])
    disp.plot()  
    
    for labels in disp.text_.ravel():
        labels.set_fontsize(15)
        labels.set_fontweight("bold")     
    
    plt.title(f"{fs_method_name}", fontsize = 15, fontweight = "bold")
    
    plt.xlabel(xlabel="Predicted Label", fontsize=15, fontweight="bold")
    plt.ylabel(ylabel="True Label", fontsize=15, fontweight="bold")
    
    plt.xticks(fontsize=15, fontweight="bold")
    plt.yticks(rotation=90, fontsize=15, fontweight="bold")
    
    plt.savefig(path_to_save_plots + fs_method_name + ".png", dpi=100)
    
    # plt.show()

    sum = 0
    for i in range(cm.shape[0]):
        sum += cm[i][i]
        
    accuracy = sum/x_test.shape[0]    
    # print(f"The accuracy of a model, trained on all features: {accuracy}\n")
    return accuracy

# global_test_size = .4113
# global_test_size = 0.3717
# global_test_size = 0.2717
global_test_size = 0.2111
# global_random_state_number = 67
# global_random_state_number = 17
# global_random_state_number = 17
global_random_state_number = 42
# This number is only for setting the maximum feature number for sequential feature selection
number_of_features_to_select = 12

ml_model_names = [
                    "CSVM",
                    "LSVM",
                    "LOGC",
                    "RIDC",                    
                    "SGDC"  
                 ]

ml_models = [
                # svm.SVC(C=5.0, 
                #         kernel='linear', 
                #         degree=1, 
                #         gamma='scale', 
                #         coef0=0.0, 
                #         tol=0.0001, 
                #         max_iter=100, 
                #         random_state=global_random_state_number),
                svm.SVC(random_state=global_random_state_number, max_iter=511),

                # svm.LinearSVC(penalty='l2', 
                #          loss='squared_hinge', 
                #          dual=True, 
                #          tol=0.0001, 
                #          C=7.0, 
                #          random_state=global_random_state_number, 
                #          max_iter=500), 
                svm.LinearSVC(random_state=global_random_state_number, max_iter=511),

                lm.LogisticRegression(penalty='l2', random_state=global_random_state_number, max_iter=511),

                lm.RidgeClassifier(random_state=global_random_state_number, max_iter=511),

                # lm.SGDClassifier(alpha=0.000915, 
                #             epsilon=0.00897,
                #             l1_ratio=0.005793, 
                #             loss='modified_huber', 
                #             penalty='L1',
                #             power_t=0.25, 
                #             tol=0.000791, 
                #             validation_fraction=0.117,
                #             random_state=global_random_state_number)
                lm.SGDClassifier(random_state=global_random_state_number, max_iter=511)
            ]

feature_selector_names = [
    "Backward Sequential",
    "Correlation Coefficient",
    "Forward Sequential",
    "Importance Coefficient"
    # "Hybrid ImCoBaSe"
]
# Regression model names for feature selection algorithms
fs_model_names = [
    "Lasso Regression",
    # "LassoCV Regression",
    "Linear Regression",
    "Logistic Regression",
    "Ridge Regression"
    # "RidgeCV Regression",
]
# Regression models for feature selection algorithms
fs_models = [   
                lm.Lasso(random_state=global_random_state_number, max_iter=537),
                lm.LinearRegression(),
                lm.LogisticRegression(random_state=global_random_state_number, max_iter=537),
                lm.Ridge(random_state=global_random_state_number, max_iter=537) 
                # lm.Lasso(alpha=0.0001791,
                #         max_iter=100,
                #         random_state=global_random_state_number,
                #         tol=0.000397
                #         ),
                        
                # lm.LassoCV(alphas=np.logspace(-6, 6, num=5),
                #                       cv=5, 
                #                       max_iter=11,
                #                       random_state=global_random_state_number,
                #                       tol=0.000397       
                #                       ),    
                
                # lm.LinearRegression(),
                
                # lm.LogisticRegression(penalty='l2', 
                #                     random_state=global_random_state_number,
                #                     max_iter=537,
                #                     tol=0.000391
                #                     ),

                # lm.Ridge(alpha=np.logspace(-6, 6, num=1), 
                #         random_state=global_random_state_number,
                #         max_iter=537,
                #         tol=0.000391
                #         ) 

                # lm.RidgeCV(alphas=np.logspace(-6, 6, num=1), cv=3)
            ]

def app():
    global number_of_features_to_select
    dataset_path = get_file_path("./")
    dataset_file_name, dataset_file_ext = get_file_name_and_ext(dataset_path)

    main_plot_dir = f"Results/{dataset_file_name}/common_plots/"
    if not os.path.exists(main_plot_dir):
        os.makedirs(main_plot_dir)
    main_doc_dir = f"Results/{dataset_file_name}/common_docs/"
    if not os.path.exists(main_doc_dir):
        os.makedirs(main_doc_dir)

    df = []
    target_name = ""

    if dataset_file_ext in ['.xls','.xlsx']:
        df = pd.read_excel(dataset_path, sheet_name="Data")
    elif dataset_file_ext == '.csv':
        df = pd.read_csv(dataset_path)

    print(f"df before preprocessing:\n{df}\n")

    if dataset_file_name in ["BreastCancerWisconsin"]:
        df = bca_wisconsin_format_fit(df)
    elif dataset_file_name in ["CBIS-DDSM-Dataset"]:
        df = CBIS_DDSM_format_fit(df)

    print(f"df after preprocessing:\n{df}\n")
    # Drops columns, which contain only 0(zero) values. 
    df = df.loc[:, (df != 0).any(axis=0)]
    # df = df.sample(n=157, random_state=42)
    print(f"DF:\n{df}")

    # df = df.iloc[:5000]
    dataset_text = f"Dataset Class Distribution Imbalance Test for\n{dataset_file_name} Dataset before Dropping Duplicate Records"
    dataset_imbalance_test(target_output=df['Pathology'], dataset_text=dataset_text, path_to_save_plots=main_plot_dir, plot_name="before")

    # Using DataFrame.drop_duplicates() to keep first duplicate row
    df = df.drop_duplicates(keep='first')
    # print(f"The dataframe after dropping duplicate records: \n{df}\n")

    # ------------------------------------------------------------------------------------------
    # These variables were only used for the dataset imbalance test task.
    target_names = df.columns[-1]
    print(f"target_names: \n{target_names}\n")
    target_output = pd.DataFrame()
    target_output[target_names] = df[target_names]
       
    # # Dataset target output class distribution imbalance test
    dataset_text = f"Dataset Class Distribution Imbalance Test for\nthe {dataset_file_name} Dataset after Dropping Duplicate Records"
    dataset_imbalance_test(target_output=target_output[target_names], dataset_text=dataset_text, path_to_save_plots=main_plot_dir, plot_name="after")
    # ------------------------------------------------------------------------------------------
        
    # Transforming categorical data features into numeric data features
    for df_col in df.columns:
        label_encoder_df_col = LabelEncoder()
        if isinstance(df[df_col].iloc[0], str):  
            # X[x_col].iloc[:] = label_encoder.fit_transform(X[x_col].iloc[:]).astype('int32')
            # df[df_col].iloc[:] = label_encoder_df_col.fit_transform(df[df_col].iloc[:]).astype('float64')
            df[df_col] = label_encoder_df_col.fit_transform(df[df_col]).astype('float64')

    target_name = "Pathology"
    # Assigning all trainable and testing features to the variable X 
    X = df.drop([target_name],axis=1)
    # scaler = MinMaxScaler()
    # scaler = StandardScaler()
    # X = pd.DataFrame(scaler.fit_transform(X.values), columns=X.columns, index=X.index)
    
    # features_names_VarThreshold = feature_selection_via_VarianceThreshold(X=X, percent=0.8)
    # X = X[features_names_VarThreshold]

    feature_names = X.columns

    # print(f"Feature names:\n{feature_names}\n")
    # Assigning target output variable to the variable y
    y = df[target_name]

    # for clf in ["c-svm", "l-svm", "logistic", "ridge", "sgdc"]:
    #     rfe_with_cv(X,y,main_plot_dir, clf)
    
    global csvm_features_to_select
    global lsvm_features_to_select
    global sgdc_features_to_select
    global logr_features_to_select
    global ridr_features_to_select

    csvm_features_to_select = 12
    lsvm_features_to_select = 12
    sgdc_features_to_select = 12
    logr_features_to_select = 12
    ridr_features_to_select = 12
    
    # Splitting the dataset into the train and test sets 
    x_train, x_test, y_train, y_test = train_test_split(X.values, df[target_name].values, \
                                        test_size = global_test_size, random_state = global_random_state_number)
    # x_train, x_test = get_minmax_normalized_X_train_test(x_train, x_test)
    # x_train, x_test = get_standard_normalized_X_train_test(x_train, x_test)  

    # X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size = global_test_size, random_state = global_random_state_number)
    # train_dataset = X_train.copy()
    # train_dataset.insert(0, target_name, Y_train)
    # _ = sns.pairplot(train_dataset, kind="reg", diag_kind="kde")

    # sub_dir_path = "withMinMaxScaling/"
    # sub_dir_path = "withoutScaling/"
    # sub_dir_path = "withStandardScaling/"
    # path_to_save_plots = "./plots/" + sub_dir_path
    # path_to_save_docs = "./docs/" + sub_dir_path

    for ml_ID in range(0, len(ml_model_names)):
        model_all_features_plot_dir = f"Results/{dataset_file_name}/{ml_model_names[ml_ID]}/"
        if not os.path.exists(model_all_features_plot_dir):
            os.makedirs(model_all_features_plot_dir)
        model_all_features_doc_dir = f"Results/{dataset_file_name}/{ml_model_names[ml_ID]}/"
        if not os.path.exists(model_all_features_doc_dir):
            os.makedirs(model_all_features_doc_dir)
        # Initializing a machine learning model. The model is support vector machines via a kernel.
        # # Here, SVC uses the gaussian kernel.
        # ml_model = SVC()              
        # print(f"The hyperparameters of the {ml_model} model: \n{ml_model.get_params()}\n")
        # Here, LinearSVC uses the linear kernel.
        ml_model = ml_models[ml_ID]         
        print(f"The hyperparameters of the {ml_model} model: \n{ml_model.get_params()}\n")
        
        # Testing a machine learning model with all features of a dataset
        acc_all_features = test_ml_model_with_all_features(model = ml_model, 
                                                        x_train = x_train, 
                                                        y_train = y_train, 
                                                        x_test = x_test, 
                                                        y_test = y_test,
                                                        fs_method_name="full_features",
                                                        path_to_save_docs=model_all_features_doc_dir,
                                                        path_to_save_plots=model_all_features_plot_dir
                                                        )
        print(f"The accuracy of the system, trained on all features: {acc_all_features}\n")
        print("End of the method **********************************************************************End of the method\n\n")
        if ml_model_names[ml_ID] == "CSVM":
            number_of_features_to_select = csvm_features_to_select
        elif ml_model_names[ml_ID] == "LSVM":
            number_of_features_to_select = lsvm_features_to_select
        elif ml_model_names[ml_ID] == "LOGC":
            number_of_features_to_select = logr_features_to_select
        elif ml_model_names[ml_ID] == "RIDC":
            number_of_features_to_select = ridr_features_to_select
        elif ml_model_names[ml_ID] == "SGDC":
            number_of_features_to_select = sgdc_features_to_select

        for fs_ID in range(0, len(fs_model_names)):
            # # Machine learning model/classifier ID
            # ml_ID = 0
            # # Feature selection model ID
            # fs_ID = 0

            plot_dir = f"Results/{dataset_file_name}/{ml_model_names[ml_ID]}/{fs_model_names[fs_ID]}/plots/"
            if not os.path.exists(plot_dir):
                os.makedirs(plot_dir)
            doc_dir = f"Results/{dataset_file_name}/{ml_model_names[ml_ID]}/{fs_model_names[fs_ID]}/docs/"
            if not os.path.exists(doc_dir):
                os.makedirs(doc_dir)
            # path_to_save_plots = plot_dir
            # path_to_save_docs = doc_dir
            
            # # Initializing a model-based feature selection algorithms using various Regression techniques
            fs_model = fs_models[fs_ID].fit(X,y)
            # print(f"Regression coefficients:{fs_model.coef_}\n")
            if fs_model_names[fs_ID] == "Logistic Regression":
                fs_model.coef_ = fs_model.coef_[0]
            print(f"The hyperparameters of the {fs_model}: \n{fs_model.get_params()}\n")  

            # Calculating feature importance coefficients using a feature selection model (fs_model).
            importance, threshold = feature_importance_coefficients(feature_select_model=fs_model)    
            # # print(f"ridge: \n{ridge}, \nimportance: {importance}, \nthreshold: {threshold}")
            display_feature_importance_coefficients(importance, feature_names, fs_model_names[fs_ID], plot_dir)

            # Select features based on the feature importance. Feature importance is calculated using the Ridge regression.
            selected_feature_names_with_importance = selecting_features_based_on_importance(X = X,
                                                                                            y = y,
                                                                                            feature_select_model = fs_model, 
                                                                                            importance = importance,
                                                                                            path_to_save_docs=doc_dir)
            # # Visualize the selected features with their distributions. The features were selected based on the average importance coefficient.
            visualize_selected_feature_distributions(X = X, 
                                                    y = y, 
                                                    selected_features = selected_feature_names_with_importance, 
                                                    target_name = target_name, 
                                                    feature_selection_method_name = "Importance Coefficients",
                                                    fs_model_name = fs_model_names[fs_ID],
                                                    path_to_save_plots = plot_dir
                                                    )
            # Testing a machine learning model with the features, selected using the selectFromModel approach
            acc_sf_importance = test_ml_model_with_selected_features(model= ml_model, 
                                                                    data_modeled = X[selected_feature_names_with_importance],
                                                                    y = y, 
                                                                    selected_features = selected_feature_names_with_importance,
                                                                    fs_method_name="importance_based_fs",
                                                                    fs_model_name=fs_model_names[fs_ID],
                                                                    path_to_save_docs=doc_dir,
                                                                    path_to_save_plots=plot_dir
                                                                    )   
            print(f"The selected features via importance coefficients: \n{selected_feature_names_with_importance} \
                    \nThe accuracy of the system, trained on the selected features based on importance: {acc_sf_importance}\n")
            plt.close('all')
            print("End of the method **********************************************************************End of the method\n\n")
            
            # Sequential feature selection via the forward feature selection approache
            forward_selected_features = forward_sequential_feature_selection(X=X, 
                                                                            y=y, 
                                                                            feature_select_model = fs_model, 
                                                                            number_of_features_to_select=number_of_features_to_select,
                                                                            path_to_save_docs=doc_dir
                                                                            )
            # Visualize the selected features with their distributions. The features were selected via forward sequential feature approach
            visualize_selected_feature_distributions(X = X, 
                                                    y = y, 
                                                    selected_features = forward_selected_features, 
                                                    target_name = target_name,
                                                    feature_selection_method_name = "Forward Sequential Approach",
                                                    fs_model_name=fs_model_names[fs_ID],
                                                    path_to_save_plots =  plot_dir
                                                    )

            # Testing a machine learning model with the features, selected using forward sequential feature approach
            acc_sf_forward = test_ml_model_with_selected_features(model = ml_model,
                                                                data_modeled = X[forward_selected_features],
                                                                y = y, 
                                                                selected_features = forward_selected_features,
                                                                fs_method_name="forward_sequential_based_fs",
                                                                fs_model_name=fs_model_names[fs_ID],
                                                                path_to_save_docs=doc_dir,
                                                                path_to_save_plots=plot_dir
                                                                )   
            print(f"The selected features via forward sequential feature selection: \n{forward_selected_features} \
                    \nThe accuracy of the system, trained on the forward selected features: {acc_sf_forward}\n")
            plt.close('all')
            print("End of the method **********************************************************************End of the method\n\n")

            # Calculating the correlation coefficients using the Pearson method
            corr = pearson_correlation_coefficients(df)   
            corr_row_number = 30
            corrDisplay = corr.iloc[0:corr_row_number, 0:corr_row_number]
            # print(f"corr: \n{corr}\n")
            
            # Heatmap display of Pearson Correlation Coeficient 
            display_pearson_correlation_coefficients(corrDisplay, plot_dir)
            # display_pearson_correlation_coefficients(corr)
            data_modeled, selected_feature_names_with_corr_coef = feature_selection_with_pearson_corr_coef(df = df, 
                                                                                                        target_ouput_name = target_name, 
                                                                                                        corr = corr,
                                                                                                        path_to_save_docs=doc_dir)
            # Visualize the selected features with their distributions. The features were selected via correlation coefficient and p-value 
            visualize_selected_feature_distributions(X = X, 
                                                    y = y, 
                                                    selected_features = selected_feature_names_with_corr_coef, 
                                                    target_name = target_name,
                                                    feature_selection_method_name = "Correlated Coefficients and p-value",
                                                    fs_model_name=fs_model_names[fs_ID],
                                                    path_to_save_plots=plot_dir
                                                    )
            # Testing a machine learning model with the features, selected using the correlation coefficient approach               
            acc_sf_corr = test_ml_model_with_selected_features(model = ml_model, 
                                                            data_modeled = data_modeled, 
                                                            y = y, 
                                                            selected_features = selected_feature_names_with_corr_coef,
                                                            fs_method_name="correlation_coefficient_based_fs",
                                                            fs_model_name=fs_model_names[fs_ID],
                                                            path_to_save_docs=doc_dir,
                                                            path_to_save_plots=plot_dir
                                                            )
            print(f"The selected features via correlation coefficients: {selected_feature_names_with_corr_coef} \
                    \nThe accuracy of the system, trained on the selected features based on correlation coef. : {acc_sf_corr}\n")
            plt.close('all')
            print("End of the method **********************************************************************End of the method\n\n")

            # Sequential feature selection via the backward feature selection approache
            backward_selected_features = backward_sequential_feature_selection(X=X, 
                                                                               y=y, 
                                                                               feature_select_model = fs_model, 
                                                                               number_of_features_to_select=number_of_features_to_select,
                                                                               path_to_save_docs=doc_dir
                                                                               )                                                                                    
            # Visualize the selected features with their distributions. The features were selected via backward sequential feature approach
            visualize_selected_feature_distributions(X = X, 
                                                     y = y, 
                                                     selected_features = backward_selected_features, 
                                                     target_name = target_name,
                                                     feature_selection_method_name = "Backward Sequential Approach",
                                                     fs_model_name=fs_model_names[fs_ID],
                                                     path_to_save_plots=plot_dir
                                                     )
            # Testing a machine learning model with the features, selected using backward sequential feature approach                                        
            acc_sf_backward = test_ml_model_with_selected_features(model = ml_model, 
                                                                   data_modeled = X[backward_selected_features],
                                                                   y = y, 
                                                                   selected_features = backward_selected_features,
                                                                   fs_method_name="backward_sequential_based_fs",
                                                                   fs_model_name=fs_model_names[fs_ID],
                                                                   path_to_save_docs=doc_dir,
                                                                   path_to_save_plots=plot_dir
                                                                   )   
            print(f"The selected features via backward sequential feature selection: {backward_selected_features} \
                    \nThe accuracy of the system, trained on the backward selected features: {acc_sf_backward}\n")
            plt.close('all')
            print("End of the method **********************************************************************End of the method\n\n")

if __name__ == "__main__":

    app()