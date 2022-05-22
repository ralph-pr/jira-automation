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
 
customFieldInfo(httpMethod: "GET", groups: ["SDLC_ADMIN", "SDLC_DEVOPSUPPORT","VDSISDLC_ADMIN","VDSISDLC_DEVOPSSUPPORT","jira-administrators", "Jira-TEMPadministrator", "SDLC_ADMIN_NTS", "SDLC_ADMIN_VES", "SDLC_ADMIN_EXAMPLEW", "SDLC_ADMIN_CMB"]) { MultivaluedMap queryParams, String body ->
     
def delegator = (DelegatorInterface) ComponentAccessor.getComponent(DelegatorInterface)
String helperName = delegator.getGroupHelperName("default");

def sqlStmt = """
Select cf.[ID], cf.[cfname], cf.[CUSTOMFIELDTYPEKEY], CAST (cf.[DESCRIPTION] AS VARCHAR(300)) As DESCRIPTION
FROM [JIRA-DC-STG].[dbo].[customfield] cf
ORDER BY [cfname] ASC
"""

def list = []

Connection conn = ConnectionFactory.getConnection(helperName);
Sql sql = new Sql(conn)

try {
    sql.eachRow(sqlStmt) {
        list << new Expando(name: it.cfname, ID: it.ID, type: it.CUSTOMFIELDTYPEKEY, description: it.DESCRIPTION.toString());
    }
    return Response.ok(new JsonBuilder(list).toString()).build();
}
finally {
    sql.close()
}
}