import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Lasso
from sklearn.model_selection import RandomizedSearchCV, KFold
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor
from sklearn.svm import SVR

def save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted) :
    # save the model statistics
    model_stats.loc[model_name,"Training_R2"] = round(current_model.score(X_train, y_train), 2)
    model_stats.loc[model_name,"Testing_R2"] = round(current_model.score(X_test, y_test), 2)
    model_stats.loc[model_name,"Training_RMSE"] = (np.sqrt(mean_squared_error(y_train, y_train_predicted)))
    model_stats.loc[model_name,"Testing_RMSE"] = (np.sqrt(mean_squared_error(y_test, y_test_predicted)))
    model_stats.loc[model_name,"Training_MBE"] = np.mean(y_train_predicted - y_train)
    model_stats.loc[model_name,"Testing_MBE"] = np.mean(y_test_predicted - y_test)

    return model_stats

def lin_reg(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    from sklearn.linear_model import LinearRegression
    # Instantiate the LR model:
    current_model = LinearRegression()
    # train the model using training data
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def lasso(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    lasso_params_grid = {'alpha': np.arange(0.001, 10, 0.05)}
    lasso_model = Lasso()

    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    # cross validation to find the best parameter (alpha)
    lasso_cv = RandomizedSearchCV(lasso_model, lasso_params_grid, cv=kf, scoring='neg_root_mean_squared_error',
                                  random_state=42)

    # train the cross validation models
    lasso_cv.fit(X_train, y_train)
    # get the best parameters
    best_params = lasso_cv.best_params_

    # train a new model with the best parameters
    current_model = Lasso(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def ridge(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    ridge_params_grid = {'alpha': np.arange(0.001, 10, 0.05)}
    ridge_model = Ridge()
    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    # cross validation to find the best parameter (alpha)
    ridge_cv = RandomizedSearchCV(ridge_model, ridge_params_grid, cv=kf, scoring='neg_root_mean_squared_error',
                                  random_state=42)
    # train the cross validation models
    ridge_cv.fit(X_train, y_train)
    # get the best parameters
    best_params = ridge_cv.best_params_
    # train a new model with the best parameters
    current_model = Ridge(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def random_forest(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    rf_regressor = RandomForestRegressor(random_state=42)
    rf_params = {'max_depth': np.arange(1, 10, 1),
                 'min_samples_split': np.arange(2, 50, 1),
                 'min_samples_leaf': np.arange(2, 50, 1),
                 'max_features': ['sqrt', 'log2']}
    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    # cross validation to find the best parameter (see rf_params)
    rf_regressor_cv = RandomizedSearchCV(rf_regressor, rf_params, cv=kf, scoring='neg_root_mean_squared_error',
                                         random_state=42)
    # train the cross validation models
    rf_regressor_cv.fit(X_train, y_train)
    # get the best parameters
    best_params = rf_regressor_cv.best_params_
    np.random.seed(42)

    # train a new model with the best parameters
    current_model = RandomForestRegressor(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def adaboost(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    #testing Adaboost model on data with reduced features
    adaboost = AdaBoostRegressor(random_state=42)
    adaboost_params = {'learning_rate' : np.arange(0.01,1.5,0.05),
                            'n_estimators': np.arange(10,200,10),
                            'loss' : ['linear', 'square', 'exponential']}

    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    adaboost_cv = RandomizedSearchCV(adaboost, adaboost_params, random_state=42, cv=kf, scoring='neg_root_mean_squared_error')
    # train the cross validation models
    adaboost_cv.fit(X_train, y_train)

    # get the best parameters
    best_params = adaboost_cv.best_params_
    # train a new model with the best parameters
    current_model = AdaBoostRegressor(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train, y_test, y_train_predicted,
                               y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def gradboost(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    gb_regressor = GradientBoostingRegressor(random_state=42)
    gb_params = dict(learning_rate=np.arange(0.05, 0.3, 0.05),
                     n_estimators=np.arange(100, 1000, 100),
                     subsample=np.arange(0.1, 0.9, 0.05),
                     max_depth=[int(i) for i in np.arange(1, 10, 1)],
                     max_features=['sqrt', 'log2'])

    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    # cross validation to find the best parameter (see rf_params)
    gb_cv = RandomizedSearchCV(gb_regressor, gb_params, random_state=42, cv=kf, scoring='neg_root_mean_squared_error')

    # train the cross validation models
    gb_cv.fit(X_train, y_train)
    # get the best parameters
    best_params = gb_cv.best_params_
    np.random.seed(42)

    # train a new model with the best parameters
    current_model = GradientBoostingRegressor(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model

def svr_(X_train, y_train, X_test, y_test, X_std, model_name, model_stats):
    svr_regressor = SVR()
    svr_params = {'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
                  'gamma': ['scale', 'auto'],
                  'C': np.arange(0.1, 5, 0.4)}

    # Create folds that are 5 chunks without shuffling the data
    kf = KFold(n_splits=5, shuffle=False)

    # cross validation to find the best parameter (see rf_params)
    svr_cv = RandomizedSearchCV(svr_regressor, svr_params, random_state=42, cv=kf, scoring='neg_root_mean_squared_error')

    # train the cross validation models
    svr_cv.fit(X_train, y_train)

    # get the best parameters
    best_params = svr_cv.best_params_
    np.random.seed(42)

    # train a new model with the best parameters
    current_model = SVR(**best_params)
    current_model.fit(X_train, y_train)

    # get the predicted y values for the model
    y_train_predicted = current_model.predict(X_train)
    y_test_predicted = current_model.predict(X_test)
    y_predicted = current_model.predict(X_std)

    # save the model statistics
    model_stats = save_outputs(model_stats, model_name, current_model, X_train, X_test, y_train,y_test, y_train_predicted, y_test_predicted)

    return model_stats, y_train_predicted, y_test_predicted, y_predicted, current_model