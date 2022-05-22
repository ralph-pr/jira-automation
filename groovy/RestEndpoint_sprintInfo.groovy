import java.sql.Connection
import groovy.sql.Sql
import org.ofbiz.core.entity.ConnectionFactory
import org.ofbiz.core.entity.DelegatorInterface
import com.onresolve.scriptrunner.runner.rest.common.CustomEndpointDelegate
import groovy.json.JsonBuilder
import groovy.transform.BaseScript
import javax.ws.rs.core.MultivaluedMap
import javax.ws.rs.core.Response
import com.atlassian.jira.component.ComponentAccessor;

@BaseScript CustomEndpointDelegate delegate
 
sprintInfo(httpMethod: "GET", groups: ["jira-users"]) { MultivaluedMap queryParams, String body ->

def delegator = (DelegatorInterface) ComponentAccessor.getComponent(DelegatorInterface)
String helperName = delegator.getGroupHelperName("default");

def sqlStmt = """
select NAME, ID
from AO_60DB71_SPRINT
WHERE CLOSED = 1
"""

def list = []
StringBuffer sb = new StringBuffer()
Connection conn = ConnectionFactory.getConnection(helperName);
Sql sql = new Sql(conn)

try {
    sql.eachRow(sqlStmt) {
        list << new Expando(name: it.NAME, ID: it.ID);
    }
    return Response.ok(new JsonBuilder(list).toString()).build();
}

finally {
    sql.close()
}
}