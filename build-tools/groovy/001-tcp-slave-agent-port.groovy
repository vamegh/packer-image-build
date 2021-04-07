/*

//This is not used

import hudson.model.*;
import jenkins.model.*;


Thread.start {
      sleep 10000
      println "--> setting agent port for jnlp"
      //def env = System.getenv()
      //int port = env['JENKINS_SLAVE_AGENT_PORT'].toInteger()
      int port = 50000
      Jenkins.instance.setSlaveAgentPort(port)
      println "--> setting agent port for jnlp... done"
}
*/