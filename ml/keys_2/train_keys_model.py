import sys, os, random
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier

my_dir = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(my_dir, '../'))
import ml_utils
import model

def main():
    X, y, train_X, train_y, test_X, test_y = ml_utils.load_data(my_dir, 0)
    estimator = RandomForestClassifier(n_estimators=40 , max_depth=5)
    estimator.fit(X, y)

    keys_model = model.Model(estimator, my_dir)
    keys_model.save(os.path.join(my_dir, "keys_model.pkl"))

if __name__ == "__main__":
    main()
