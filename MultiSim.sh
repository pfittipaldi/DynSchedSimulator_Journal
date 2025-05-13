python Scripts/GenerateInputFiles.py
for infile in $(ls Sim_in*.py)
do
	echo "$infile"
	string1=${infile%.py}
    	string2=${string1#Sim_inputs_}
	rm Simulator/User_Input.py
    	cp $infile Simulator/User_Input.py
	python Simulator/StabPlot.py
	mkdir $string2
	mv $infile $string2/
        mv *.pdf $string2/
        mv *.npz $string2/
done
