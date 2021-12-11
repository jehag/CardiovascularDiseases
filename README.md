# CardiovascularDiseases
An AI that determines if a patient has a heart disease depending on other health propreties.

The project is in the Jupyter Source File named Projet A2021
We show how we analysed the data to let us pick the best model.

The other Jupyter Source File, findBestCutoff, is to find the best
cutoff for our model. We ran the test locally and used the one with
the highest accuracy.

The script creator is a python script to help us confirm we chose
the best model. It created a text file that we copied in Julia.
(Don't run it, it takes hours to compile)

The train file is to help us find the best model. We partitionned
our data to be able to run tests locally.

The test file is where all the patients we have to evaluate are
located in.

The benchmark_predictions file is where we write the answer to our
predictions and submit them on Kaggle.

We ended up in second place out of more than 50 students.