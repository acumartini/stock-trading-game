from agents.models import Agent

from lib.django_cron import cronScheduler, Job

class AgentExecuteCheck(Job):
    # Run every 30 seconds
    run_every = 30
        
    def job(self):
        # This will be executed every 5 minutes
        print '\nBegin - Executing Agent Actions'

        for agent in Agent.objects.select_subclasses():
        	print "\nProcessing Agent - " + str(agent)
        	if agent.ready_to_execute():
        		print "ready_to_execute = True"
        		print "begin - executing"
        		agent.execute()
        		print "finished - executing"
    		else:
    			print "ready_to_execute = False"
        
        print '\nEnd - Executing Agent Actions'


cronScheduler.register(AgentExecuteCheck)