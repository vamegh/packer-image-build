/*
   Copyright (c) 2015-2018 Sam Gleske - https://github.com/samrocketman/jenkins-bootstrap-jervis

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   */

/*
   Configures GitHub as the security realm from the GitHub Authentication
   Plugin (github-oauth).

   github-oauth 0.29
 */

import hudson.security.SecurityRealm
import org.jenkinsci.plugins.GithubSecurityRealm
import net.sf.json.JSONObject
import groovy.json.*

def parseJson(String configuration) {
    return new JsonSlurperClassic().parseText(configuration)
}

String config_data =  new File(config_file).text
def github_config = parseJson(config_data)

if(!(github_config instanceof Map)) {
    throw new Exception('github_config must be a Map.')
}

github_config = github_config as JSONObject

String githubWebUri = github_config.optString('web_uri', GithubSecurityRealm.DEFAULT_WEB_URI)
String githubApiUri = github_config.optString('api_uri', GithubSecurityRealm.DEFAULT_API_URI)
String oauthScopes = github_config.optString('oauth_scopes', GithubSecurityRealm.DEFAULT_OAUTH_SCOPES)
String clientID = github_config.optString('client_id')
String clientSecret = github_config.optString('client_secret')

if(!Jenkins.instance.isQuietingDown()) {
    if(clientID && clientSecret) {
        SecurityRealm github_realm = new GithubSecurityRealm(githubWebUri, githubApiUri, clientID, clientSecret, oauthScopes)
        //check for equality, no need to modify the runtime if no settings changed
        if(!github_realm.equals(Jenkins.instance.getSecurityRealm())) {
            Jenkins.instance.setSecurityRealm(github_realm)
            Jenkins.instance.save()
            println 'Security realm configuration has changed.  Configured GitHub security realm.'
        } else {
            println 'Nothing changed.  GitHub security realm already configured.'
        }
    }
} else {
    println 'Shutdown mode enabled.  Configure GitHub security realm SKIPPED.'
}




