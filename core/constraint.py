class Constraint:
    # TODO: extend + statistic
    VALUES = []

    def __init__(self, include_all=False, include_custom=False):
        self.include_all = include_all
        self.include_custom = include_custom
        self.auto_analyze_constraint()

    def auto_analyze_constraint(self):
        if self.include_custom:
            Constraint.VALUES += [
                'com.kms.katalon.core.main.ScriptEngine.run',
                'com.kms.katalon.core.main.ScriptEngine.runScriptAsRawText',
                'com.kms.katalon.core.main.TestCaseExecutor.runScript',
                'com.kms.katalon.core.main.TestCaseExecutor.doExecute',
                'com.kms.katalon.core.main.TestCaseExecutor.processExecutionPhase',
                'com.kms.katalon.core.main.TestCaseExecutor.accessMainPhase',
                'com.kms.katalon.core.main.TestCaseExecutor.execute',
                'com.kms.katalon.core.main.TestSuiteExecutor.accessTestCaseMainPhase',
                'com.kms.katalon.core.main.TestSuiteExecutor.accessTestSuiteMainPhase',
                'com.kms.katalon.core.main.TestSuiteExecutor.execute',
                'com.kms.katalon.core.main.TestCaseMain.startTestSuite',
                'com.kms.katalon.core.main.TestCaseMain$startTestSuite$0.call',
            ]
