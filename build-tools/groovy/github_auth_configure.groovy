
// vhedayati

import hudson.security.AuthorizationStrategy
import org.jenkinsci.plugins.GithubAuthorizationStrategy
import net.sf.json.JSONObject
import groovy.json.*


def parseJson(String configuration) {
    return new JsonSlurperClassic().parseText(configuration)
}

String config_data =  new File(config_file).text
def github_auth = parseJson(config_data)

if(!(github_auth instanceof Map)) {
    throw new Exception('github_auth must be a Map.')
}

github_auth = github_auth as JSONObject

String adminUserNames = github_auth.optString('admin_users')
String organizationNames = github_auth.optString('org_name', 'ev9')
boolean useRepositoryPermissions = github_auth.optBoolean('use_repo_perms', true)
boolean authenticatedUserReadPermission = github_auth.optBoolean('auth_read', false)
boolean authenticatedUserCreateJobPermission = github_auth.optBoolean('auth_create', false)
boolean allowGithubWebHookPermission = github_auth.optBoolean('webhook_read', false)
boolean allowCcTrayPermission = github_auth.optBoolean('cc_read', false)
boolean allowAnonymousReadPermission = github_auth.optBoolean('anon_read', false)
boolean allowAnonymousJobStatusPermission = github_auth.optBoolean('anon_view', false)

AuthorizationStrategy github_authorization = new GithubAuthorizationStrategy(adminUserNames,
        authenticatedUserReadPermission,
        useRepositoryPermissions,
        authenticatedUserCreateJobPermission,
        organizationNames,
        allowGithubWebHookPermission,
        allowCcTrayPermission,
        allowAnonymousReadPermission,
        allowAnonymousJobStatusPermission)

//check for equality, no need to modify the runtime if no settings changed
if(!github_authorization.equals(Jenkins.instance.getAuthorizationStrategy())) {
    Jenkins.instance.setAuthorizationStrategy(github_authorization)
    Jenkins.instance.save()
    println 'Auth Strategy configuration has changed.  Configured GitHub Auth Strategy'
} else {
    println 'Nothing changed.  GitHub Auth Strategy already configured.'
}
