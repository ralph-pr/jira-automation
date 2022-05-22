import org.apache.log4j.Level
import org.apache.log4j.Logger
import groovy.time.*;

Date date = new Date();

Logger log = log
log.setLevel(Level.DEBUG)
log.debug "Starting @ " + date.format("MM/dd/yyyy HH:mm");

def finalMsg = "";

// Define a function to do the work
def testUrlResponse(String URL){
	// GET
	def get = new URL(URL).openConnection();
	def getRC = get.getResponseCode();
	log.debug("rc=" + getRC);
	def respLen = -1;
	if(getRC.equals(200)) {
		respLen = get.getInputStream().getText().length();
		log.debug("len=" + respLen);
	}
	else 
	{
		log.debug("error");
	}
	
	return "<test><url>" + URL + "</url><rc>" + getRC + "</rc><len>" + respLen + "<len></test>";
}

// The line below can be generated in Excel or SQL from a list of project names, IDs, keys.
finalMsg += testUrlResponse("https://mejira.example.com");
finalMsg += testUrlResponse("https://oneconfluence.example.com");

// wrap it up - we're done!
finalMsg += "...Finished";

log.debug finalMsg;

