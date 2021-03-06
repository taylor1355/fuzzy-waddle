import sys, os, random
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import learning_curve
from sklearn.model_selection import validation_curve
from sklearn.model_selection import PredefinedSplit

import ml_utils

import warnings
warnings.filterwarnings(action='ignore')

TEST_FRACTION = 0.2
CV_FOLDS = 5

class Algorithm:
    def __init__(self, name, params, model):
        self.name = name
        self.params = params
        self.base_model = model

    def optimize_params(self, model, X, y, dir):
        param_grid = {param.actual_name: param.values for param in self.params}
        grid_search = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=1)
        grid_search.fit(X, y)

        return grid_search

    def learning_curve(self, model, X, y, split, dir):
        curve = plot_learning_curve(model, self.name + " Learning Curve", X, y, split)
        curve.savefig(os.path.join(dir, self.name + " Learning Curve.png"))

    def validation_curves(self, model, X, y, dir):
        for i in range(len(self.params)):
            plot_param = self.params[i].copy()
            curve = plot_validation_curve(model, plot_param, self.name + " Validation Curve", X, y)
            curve.savefig(os.path.join(dir, self.name + " Validation Curve " + str(i + 1) + ".png"))

class Parameter:
    def __init__(self, human_name, actual_name, values, numeric_values=None, log_scale=False):
        self.human_name = human_name
        self.actual_name = actual_name
        self.values = values
        self.numeric_values = numeric_values
        self.log_scale=log_scale

    def copy(self):
        numeric_values = None if self.numeric_values is None else list(self.numeric_values)
        return Parameter(self.human_name, self.actual_name, list(self.values), numeric_values, self.log_scale)

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <task directory>".format(sys.argv[0]))
        return

    task_dir = sys.argv[1]
    X, y, train_X, train_y, test_X, test_y = ml_utils.load_data(task_dir, TEST_FRACTION)
    curr_results_dir = os.path.join(task_dir, "results")

    # # Boosted Decision Tree
    # num_estimators_param = Parameter("Max Number of Estimators", "n_estimators", range(10, 111, 10))
    # base_estimators = [DecisionTreeClassifier(max_depth=d) for d in range(2, 6)]
    # estimator_depth_param = Parameter("Max Tree Depth", "base_estimator", base_estimators, range(1, 6))
    # boosted_algo = Algorithm("Boosted Decision Tree", [num_estimators_param, estimator_depth_param], AdaBoostClassifier())
    # analyze_algorithm(boosted_algo, curr_results_dir, train_X, train_y, X, y)
    # print()

    # Random Forest
    num_estimators_param = Parameter("Number of Estimators", "n_estimators", range(1, 121, 10))
    max_depth = Parameter("Max Tree Depth", "max_depth", range(1, 7))
    rf_algo = Algorithm("Random Forest", [num_estimators_param, max_depth], RandomForestClassifier())
    analyze_algorithm(rf_algo, curr_results_dir, train_X, train_y, X, y)
    print()

    # Naiive Bayes
    bayes_algo = Algorithm("Naiive Bayes", [], GaussianNB())
    analyze_algorithm(bayes_algo, curr_results_dir, train_X, train_y, X, y)
    print()

    # Support Vector Machine (Linear)
    c_param = Parameter("C Value", "C", [1e-2, 1e-1, 1e0, 1e1, 1e2], log_scale=True)
    linear_svm_algo = Algorithm("Linear Support Vector Machine", [c_param], svm.SVC(kernel="linear"))
    analyze_algorithm(linear_svm_algo, curr_results_dir, train_X, train_y, X, y)
    print()

    # Linear Discriminant Analysis
    lda_algo = Algorithm("Linear Discriminant Analysis", [], LinearDiscriminantAnalysis())
    analyze_algorithm(lda_algo, curr_results_dir, train_X, train_y, X, y)
    print()

    # Neural Network
    hidden_layer_param = Parameter("Number of Hidden Layers", "hidden_layer_sizes", vary_num_hidden_layers(30, 5), range(1, 6))
    alpha_param = Parameter("Regularization Strength (alpha)", "alpha", [1e0, 1e-2, 1e-4, 1e-6, 1e-8], log_scale=True)
    nn_algo = Algorithm("Neural Network", [hidden_layer_param, alpha_param], MLPClassifier(max_iter=5000))
    analyze_algorithm(nn_algo, curr_results_dir, train_X, train_y, X, y)
    print()


def analyze_algorithm(algorithm, dir, train_X, train_y, X, y):
    start_time = timer()
    print("Started analysis of " + algorithm.name)

    algorithm_dir = os.path.join(dir, algorithm.name)
    create_dir_if_needed(algorithm_dir)

    grid_search = algorithm.optimize_params(algorithm.base_model, train_X, train_y, algorithm_dir)
    print("Finished grid search in " + elapsed_time(start_time))

    learning_curve_start_time = timer()
    split = PredefinedSplit(test_fold=[-1 if i < len(train_X) else 0 for i in range(len(X))])
    algorithm.learning_curve(grid_search.best_estimator_, X, y, split, algorithm_dir)
    print("Finished learning curve in " + elapsed_time(learning_curve_start_time))

    validation_curve_start_time = timer()
    algorithm.validation_curves(grid_search.best_estimator_, train_X, train_y, algorithm_dir)
    print("Finished validation curves in " + elapsed_time(validation_curve_start_time))

    print("Finished analysis in " + elapsed_time(start_time))

def vary_num_hidden_layers(layer_size, max_layers):
    layer_specs = []
    single_layer = (layer_size,)
    layer_spec = ()
    for i in range(max_layers):
        layer_spec = layer_spec + single_layer
        layer_specs.append(layer_spec)
    return layer_specs

def elapsed_time(start_time):
    return str(timer() - start_time) + " sec"

def plot_learning_curve(estimator, title, X, y, split):
    plt.figure()
    plt.title(title)
    plt.xlabel("Training examples")
    plt.ylabel("Score")

    steps = 6
    train_sizes = [(i+1)/steps for i in range(steps)]
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=split, n_jobs=1, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Test score")

    plt.legend(loc="best")
    return plt

def plot_validation_curve(estimator, param, title, X, y):
    plt.figure()
    plt.title(title)
    plt.xlabel(param.human_name)
    plt.ylabel("Score")

    param_numeric_values = param.values if param.numeric_values is None else param.numeric_values
    train_scores, test_scores = validation_curve(
        estimator, X, y, param_name=param.actual_name, param_range=param.values,
        cv=CV_FOLDS, scoring="accuracy", n_jobs=1)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.grid()

    if param.log_scale:
        plt.xscale('log')

    plt.fill_between(param_numeric_values, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(param_numeric_values, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(param_numeric_values, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(param_numeric_values, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

def create_dir_if_needed(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

if __name__ == "__main__":
    main()
