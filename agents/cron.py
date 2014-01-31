from agents.models import Agent

from lib.django_cron import cronScheduler, Job

class AgentExecuteCheck(Job):
    run_every = 60
        
    def job(self):
        print '\nBegin - Executing Agent Actions'

        for agent in Agent.objects.select_subclasses():
            print "\nProcessing Agent - " + str(agent)
            try:
                if agent.ready_to_execute():
                    print "ready_to_execute = True"
                    print "begin - executing"
                    agent.execute()
                    print "finished - executing"
                else:
                    print "ready_to_execute = False"
            except:
                print "Caught unknown error from agent: %s" % str(agent)
                    
        print '\nEnd - Executing Agent Actions'


cronScheduler.register(AgentExecuteCheck)