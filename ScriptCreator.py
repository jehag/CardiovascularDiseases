import itertools

liste = ["ChestPainType", "OldpeakGroups", "AgeGroups", "CholesterolGroups", "MaxHRGroups", "Sex", "RestingECG", "FastingBS", "ExerciseAngina", "STSlope"]
imports = """using CSV, DataFrames, Gadfly, GLM, Statistics, Distributions, LinearAlgebra, Random
ENV["COLUMNS"] = 1000;
full = CSV.read("train.csv", DataFrame);
"""

real = """
every = DataFrame(A = String[], B = Float64[])
all = []

function findCutoff(table, column, newColumn, lowRange, highRange, nIteration, reverse=false)
    tempTable = select(table, column, newColumn, :HeartDisease)
    maxValue = 0
    maxIt = 0
    minValue = 1.0
    minIt = 0
    minmaxValue = 0
    minmaxIt = 0
    if lowRange >= highRange
        error("range invalid")
    end
    n = size(table, 1)
    for l in 0.0:nIteration
        j = lowRange + ((highRange - lowRange)/nIteration * l) # itère nIteration fois entre lowRange et highRange
        for i in 1:n
            if table[!,column] != Missing && table[!,column][i] < j #selon la valeur de j, on classe les données
                table[!,newColumn][i] = reverse ? "1" : "0" #on swap les classes si c'est inversement proportionnel pour les meilleurs seuils
            else
                table[!,newColumn][i] = reverse ? "0" : "1"
            end
        end
        tempTable = combine(groupby(table, [newColumn]), :HeartDisease => mean => :Odds) 

        if size(tempTable, 1) > 1
            if tempTable.Odds[1] < minValue # on trouve le meilleur seuil pour la classe 0
                minIt = j
                minValue = tempTable.Odds[1]
            end 

            if tempTable.Odds[2] > maxValue # on trouve le meilleur seuil pour la classe 1
                maxIt = j
                maxValue = tempTable.Odds[2] 
            end 

            # on trouve le meilleur seuil pour le produit des 2 classes, pour un seuil acceptable à la fois pour les classes 1 et 2
            if (1 - tempTable.Odds[1]) * tempTable.Odds[2] > minmaxValue && tempTable.Odds[1] != 0 && tempTable.Odds[2] != 1
                minmaxIt = j
                minmaxValue = (1 - tempTable.Odds[1]) * tempTable.Odds[2]
            end 
        end 
    end
    return [[
        minIt,
        minValue],[
        maxIt,
        maxValue],[
        minmaxIt,
        minmaxValue
    ]]
end

function before!()
    global full = full[shuffle(1:size(full, 1)),:];
    full[!, :FastingBS] = string.(full[:, :FastingBS]);
    number = size(full, 1);
    twoThirds = floor(Int, 2/3*number);
    global data = first(full,twoThirds);
    estimate = last(full, number-twoThirds);

    data[:, :OldpeakGroups] .= "2"
    global oldPeakCutoffs = findCutoff(data, :Oldpeak, :OldpeakGroups, 0.0, 2.0, 2000.0)
    data[:, :AgeGroups] .= "2"
    global ageCutoff = findCutoff(data, :Age, :AgeGroups, 0.0, 100.0, 1000.0)
    data[:, :CholesterolGroups] .= "2" 
    data[:, :MaxHRGroups] .= "2"
    global maxHRCutoffs = findCutoff(data, :MaxHR, :MaxHRGroups, 50.0, 200.0, 2000.0, true)

    for i in 1:size(data,1)
        if data.Oldpeak[i] < 0.801
            data.OldpeakGroups[i] = "0"
        else
            data.OldpeakGroups[i] = "1"
        end
        if data.Age[i] < 37.1
            data.AgeGroups[i] = "0"
        else
            data.AgeGroups[i] = "1"
        end
        if ismissing(data.Cholesterol[i])
            data.CholesterolGroups[i] = "0"
        else
            data.CholesterolGroups[i] = "1"
        end
        if(data.MaxHR[i] < 176.075)
            data.MaxHRGroups[i] = "0"
        else
            data.MaxHRGroups[i] = "1"
        end
    end
    return estimate
end

function after!(estimate)
    estimate[:, :OldpeakGroups] .= "2"
    estimate[:, :AgeGroups] .= "2"
    estimate[:, :CholesterolGroups] .= "2" 
    estimate[:, :MaxHRGroups] .= "2"
    for i in 1:size(estimate,1)
        if estimate.Oldpeak[i] < 0.801
            estimate.OldpeakGroups[i] = "0"
        else
            estimate.OldpeakGroups[i] = "1"
        end
        if estimate.Age[i] < 37.1
            estimate.AgeGroups[i] = "0"
        else
            estimate.AgeGroups[i] = "1"
        end
        if ismissing(estimate.Cholesterol[i])
            estimate.CholesterolGroups[i] = "0"
        else
            estimate.CholesterolGroups[i] = "1"
        end
        if(estimate.MaxHR[i] < 176.075)
            estimate.MaxHRGroups[i] = "0"
        else
            estimate.MaxHRGroups[i] = "1"
        end
    end

    thetaestimate = predict(M, estimate)

    seuil = 0.5

    counter = 0

    for i in 1:size(estimate,1)
        if (thetaestimate[i] >= seuil && estimate[i, :].HeartDisease == 1)
            counter = counter + 1
        elseif (thetaestimate[i] < seuil && estimate[i, :].HeartDisease == 0)
            counter = counter + 1
        end
    end

    push!(all,counter/size(estimate,1))
end 

function meaan!()
    global youngSum = 0
    youngBlood = 0
    for i in 1:size(all,1)
        if all[i] > youngBlood
            youngBlood = all[i]
        end
        youngSum = all[i] + youngSum
    end
end
"""
fake = """
for i in 1:5
    estimate = before!()
    global M = glm(@formula(HeartDisease ~ {formule}), data,  Bernoulli(), LogitLink())
    after!(estimate)
end
meaan!()
push!(every, ("{formule}", youngSum/size(all,1)))
all = []
"""

n = 0
with open('juliaScript.txt', 'w') as f:
    f.write(imports)
    f.write(real)
    for L in range(0, len(liste)+1):
        for subset in itertools.combinations(liste, L):
            tool = ""
            for i in subset:
                tool += i + " + "
            tool = tool[:-3]
            if (tool != ""):
                f.write(fake.format(formule=tool))
            n += 1

print(n)



