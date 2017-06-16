#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy as np
import multiprocessing
import matplotlib.pyplot as plt
from pandas import DataFrame,Series
from sklearn import metrics
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from ChicagoBoothML_Helpy.EvaluationMetrics import bin_classif_eval

def train_test(X_train,X_test,y_train,y_test):
    #-----------------------------Find the best parameters' combination of the model------------------------------
    #param_test1 = {'n_estimators': range(20, 600, 20)}
    #gsearch1 = GridSearchCV(estimator=RandomForestClassifier(min_samples_split=200,
    #                                                         min_samples_leaf=2, max_depth=5, max_features='sqrt',
    #                                                         random_state=19),
    #                        param_grid=param_test1, scoring='roc_auc', cv=5)
    #gsearch1.fit(X_train,y_train)
    #for item in gsearch1.grid_scores_:
    #    print(item)
    #print(gsearch1.best_params_)
    #print(gsearch1.best_score_)
    #print(gsearch1.grid_scores_, gsearch1.best_params_, gsearch2.best_score_,'\n')
    # print('-----------------------------------------------------------------------------------------------------')
    # param_test2 = {'max_depth': range(2, 16, 2), 'min_samples_split': range(20, 200, 20)}
    # gsearch2 = GridSearchCV(estimator=RandomForestClassifier(n_estimators=300,
    #                                                          min_samples_leaf=2, max_features='sqrt', oob_score=True,
    #                                                          random_state=19),
    #                         param_grid=param_test2, scoring='roc_auc', iid=False, cv=5)
    # gsearch2.fit(X_train,y_train)
    # for item in gsearch2.grid_scores_:
    #    print(item)
    # print(gsearch2.best_params_)
    # print(gsearch2.best_score_)
    # print(gsearch2.cv_results_, gsearch2.best_params_, gsearch2.best_score_,'\n')
    ##-----------------------------Find the best parameters' combination of the model------------------------------
    B = 300
    RANDOM_SEED = 99
    model = \
        RandomForestClassifier(
            n_estimators=B,
            #criterion='entropy',
            criterion='gini',
            #max_depth=None,  # expand until all leaves are pure or contain < MIN_SAMPLES_SPLIT samples
            max_depth=4,
            min_samples_split=80,
            min_samples_leaf=2,
            min_weight_fraction_leaf=0.0,
            #max_features=None, # number of features to consider when looking for the best split; None: max_features=n_features
            max_features="sqrt",
            max_leaf_nodes=None,  # None: unlimited number of leaf nodes
            bootstrap=True,
            oob_score=True,  # estimate Out-of-Bag Cross Entropy
            n_jobs=multiprocessing.cpu_count() - 4,  # paralellize over all CPU cores minus 4
            class_weight=None,  # our classes are skewed, but but too skewed
            random_state=RANDOM_SEED,
            verbose=0,
            warm_start=False)

    kfold = model_selection.KFold(n_splits=5,random_state=RANDOM_SEED)
    eval_standard = ['accuracy','recall_macro','precision_macro','f1_macro']
    results = []
    for scoring in eval_standard:
        cv_results = model_selection.cross_val_score(model,X_train,y_train,scoring=scoring,cv=kfold)
        results.append(cv_results)
        msg = "%s: %f (%f)" % (scoring,cv_results.mean(),cv_results.std())
        print(msg)
    # Make predictions on validation dataset
    model.fit(X_train,y_train)
    print('oob_score: %f' % (model.oob_score_))
    #default evaluation way
    print('-------------------default evaluation----------------------')
    rf_pred_probs = model.predict(X=X_test)
    result_probs = np.column_stack((rf_pred_probs,y_test.as_matrix()))
    #for item in result_probs:
    #  print(item)
    print("confusion_matrix:\n",metrics.confusion_matrix(y_test, rf_pred_probs))
    print("accuracy_score:",metrics.accuracy_score(y_test, rf_pred_probs))
    print("recall_score:",metrics.recall_score(y_test, rf_pred_probs))
    print("precision_score:",metrics.precision_score(y_test, rf_pred_probs))
    print("f1_score:",metrics.f1_score(y_test, rf_pred_probs))
    print("roc_auc_score:",metrics.roc_auc_score(y_test, rf_pred_probs))
    print("classification_report:\n",metrics.classification_report(y_test, rf_pred_probs))

    rf_pred_probs = model.predict_proba(X=X_test)
    result_probs = np.column_stack((rf_pred_probs,y_test.as_matrix()))
    #for item in result_probs:
    #   print(item)
    result_df = DataFrame(result_probs,columns=['pred_neg','pred_pos','real'])
    #fpr,tpr,thresholds = metrics.roc_curve(result_df['real'],result_df['pred_pos'],pos_label=2)
    fpr,tpr,_ = metrics.roc_curve(result_df['real'],result_df['pred_pos'])
    # good model's auc should > 0.5
    print("auc:",metrics.auc(fpr,tpr))
    # good model's ks should > 0.2
    print("ks:",max(tpr-fpr))
    # good model's gini should > 0.6
    print("gini:",2*metrics.auc(fpr,tpr)-1)

    #self-defined evaluation way
    print('-------------------self-defined evaluation----------------------')
    low_prob = 1e-6
    high_prob = 1 - low_prob
    log_low_prob = np.log(low_prob)
    g_low_prob = np.log(low_prob)
    log_high_prob = np.log(high_prob)
    log_prob_thresholds = np.linspace(start=log_low_prob,stop=log_high_prob,num=100)
    prob_thresholds = np.exp(log_prob_thresholds)
    rf_pred_probs = model.predict_proba(X=X_test)
    #result_probs = np.column_stack((rf_pred_probs,y_test))
    #for item in result_probs:
    #    print(item)
    #for item in rf_pred_probs[:,1]:
    #    print(item)

    ## histogram of predicted probabilities
    ##n,bins,patches = plt.hist(rf_pred_probs[:1],10,normed=1,facecolor='g',alpha=0.75)
    ##plt.xlabel('Predicted probability of diabetes')
    ##plt.ylabel('Frequency')
    ##plt.title('Histogram of predicted probabilities')
    ###plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    ##plt.axis([0,1,0,1])
    ##plt.grid(True)

    #print(type(rf_pred_probs))
    #print(type(rf_pred_probs[:,1]))
    #print(rf_pred_probs[:,1])
    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #ax.hist(rf_pred_probs[:,1], bins=20)
    #plt.xlim(0,1)
    #plt.title('Histogram of predicted probabilities')
    #plt.xlabel('Predicted probability of diabetes')
    #plt.ylabel('Frequency')
    #plt.show()

    model_oos_performance = bin_classif_eval(rf_pred_probs[:,1],y_test,pos_cat=1,thresholds=prob_thresholds)
    #print(type(model_oos_performance))
    #for item in model_oos_performance.recall:
    #    print(item)
    recall_threshold = .74
    idx = next(i for i in range(100) if model_oos_performance.recall[i] <= recall_threshold) - 1
    print("idx = %d" % idx)
    selected_prob_threshold = prob_thresholds[idx]
    print("selected_prob_threshold:", selected_prob_threshold)
    print(model_oos_performance.iloc[idx,:])

def train_test1(X_train,X_test,y_train,y_test):
    B=10
    parameters = {'n_estimators':[10],'criterion':['gini']}
    best_parameters = {}
    model = \
        RandomForestClassifier(
            n_estimators=B,
            criterion='gini',
            class_weight='balanced',
            warm_start=False)
    grid_cv = GridSearchCV(model,parameters)
    grid_cv.fit(X_train,y_train)
    print('best_score_:',grid_cv.best_score_)
    print('best_estimator_:',grid_cv.best_estimator_)
    rf_pred_probs = grid_cv.predict(X=X_test)
    result_probs = np.column_stack((rf_pred_probs,y_test.as_matrix()))
    #for item in result_probs:
    #  print(item)
    print("confusion_matrix:\n",metrics.confusion_matrix(y_test, rf_pred_probs))
    print("accuracy_score:",metrics.accuracy_score(y_test, rf_pred_probs))
    print("recall_score:",metrics.recall_score(y_test, rf_pred_probs))
    print("precision_score:",metrics.precision_score(y_test, rf_pred_probs))
    print("f1_score:",metrics.f1_score(y_test, rf_pred_probs))
    print("roc_auc_score:",metrics.roc_auc_score(y_test, rf_pred_probs))
    print("classification_report:\n",metrics.classification_report(y_test, rf_pred_probs))

    rf_pred_probs = grid_cv.predict_proba(X=X_test)
    result_probs = np.column_stack((rf_pred_probs,y_test.as_matrix()))
    #for item in result_probs:
    #   print(item)
    result_df = DataFrame(result_probs,columns=['pred_neg','pred_pos','real'])
    #fpr,tpr,thresholds = metrics.roc_curve(result_df['real'],result_df['pred_pos'],pos_label=2)
    fpr,tpr,_ = metrics.roc_curve(result_df['real'],result_df['pred_pos'])
    # good model's auc should > 0.5
    print("auc:",metrics.auc(fpr,tpr))
    # good model's ks should > 0.2
    print("ks:",max(tpr-fpr))
    # good model's gini should > 0.6
    print("gini:",2*metrics.auc(fpr,tpr)-1)
