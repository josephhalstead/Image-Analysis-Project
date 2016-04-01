var laneNum =0; //global var of how many lanes to analyse.

macro "Create Lanes" {

	run("Subtract Background...", "rolling=50 light"); // subtract background to see lanes better
	//makeRectangle(60, 174, 202, 1236); // auto plot, but can select first rectangle manually.
	run("Select First Lane");
	Roi.getBounds(x,y,w,h); //get details of first rectangle
	laneNum = getNumber("How many lanes?", 0); //how many lanes should we look at

	for (i=1; i<laneNum; i++){ //create a series of rectangles itertively along width of image
		makeRectangle(x+(i*w), y, w, h); //draw rectangle to the left of the previous
		run("Select Next Lane"); //mark as next lane
}
// stop to allow manual adjustment	
}
macro "Analyse Data" {

	//macro plots lanes as intensity graphs then converts these images to XY date that can be saved to a text file.

	
	path=getDirectory("Select a directory to save the created files."); //Where should we save files

	run("Plot Lanes"); //create graph of lanes based on intensity along length nb - all graphs together
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec); //for file name

	getDimensions(width, height,c,s,f); //get graph dimensions

	for (i=0; i<laneNum; i++){ //loop splits graph into sections based on how many lanes there were
		makeRectangle(0, 16+i*((height-16)/laneNum)+1, width, ((height-16)/laneNum)-3); //draw rectangle below previous
		run("Profile Plot Options...", 
     	"width=450 height=200 auto-close list interpolate draw"); 
		run("Analyze Line Graph"); //turn to XY data 
		selectWindow("Plot Values"); 
		values = getInfo();
		run("Close");
		f = File.open(path+year+"-"+month+"-"+dayOfMonth+"-"+"Lane-" +(i+1)+".txt"); //save data to file
    	print(f, values); 
		File.close(f);

		}

		close() //close graph window
}
