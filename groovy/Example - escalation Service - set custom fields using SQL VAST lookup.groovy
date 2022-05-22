import com.atlassian.jira.component.ComponentAccessor

//TO-DO: lookup values by SQL call to VAST
def stringApplId = 'new.2.value.from.code'
def stringPortfolio = 'GTS'
def stringVped = 'Other'	// Nanda Kumar Other

//Handle Appl ID
def cfApplId = customFieldManager.getCustomFieldObjects(issue).find {it.name == 'Appl ID'}
def applId = stringApplId
issueInputParameters.addCustomFieldValue(cfApplId.id, applId)
log.warn("cfApplId set to " + applId)

//Handle Portfolio
def cfPortfolio = customFieldManager.getCustomFieldObjects(issue).find {it.name == 'Portfolio'}
def fieldConfig = cfPortfolio.getRelevantConfig(issue)
Long portfolio = ComponentAccessor.getOptionsManager().getOptions(fieldConfig).getOptionForValue(stringPortfolio, null).getOptionId()
issueInputParameters.addCustomFieldValue(cfPortfolio.id, portfolio.toString())
log.warn("cfPortfolio set to " + portfolio)

//Handle VP / Exec Dir
def cfVp = customFieldManager.getCustomFieldObjects(issue).find {it.name == 'VP/Exec Dir'}
fieldConfig = cfVp.getRelevantConfig(issue)
Long vped = ComponentAccessor.getOptionsManager().getOptions(fieldConfig).getOptionForValue(stringVped, null).getOptionId()
issueInputParameters.addCustomFieldValue(cfVp.id, vped.toString())
log.warn("cfVp set to " + vped)