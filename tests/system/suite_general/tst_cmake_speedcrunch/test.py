source(findFile("scripts", "qtcreator.py"))

SpeedCrunchPath = ""
buildFinished = False
buildSucceeded = False

def handleBuildFinished(object, success):
    global buildFinished, buildSucceeded
    buildFinished = True
    buildSucceeded = success

def main():
    if(which("cmake") == None):
        test.fatal("cmake not found")
        return

    startApplication("qtcreator" + SettingsPath)

    invokeMenuItem("File", "Open File or Project...")

    test.verify(os.path.exists(SpeedCrunchPath))
    waitForObject("{name='QFileDialog' type='QFileDialog' visible='1' windowTitle='Open File'}", 20000)
    type(findObject("{name='fileNameEdit' type='QLineEdit'}"), SpeedCrunchPath)
    clickButton(findObject("{text='Open' type='QPushButton'}"))

    clickButton(waitForObject(":CMake Wizard.Next_QPushButton", 20000))
    clickButton(waitForObject(":CMake Wizard.Run CMake_QPushButton", 20000))
    clickButton(waitForObject(":CMake Wizard.Finish_QPushButton", 60000))

    waitFor("object.exists(':speedcrunch_QModelIndex')", 20000)

    # Test that some of the expected items are in the navigation tree
    for row, record in enumerate(testData.dataset("speedcrunch_tree.tsv")):
        node = testData.field(record, "node")
        value = testData.field(record, "value")
        test.compare(findObject(node).text, value)

    # Invoke a rebuild of the application
    installLazySignalHandler("{type='ProjectExplorer::BuildManager'}", "buildQueueFinished(bool)", "handleBuildFinished")
    invokeMenuItem("Build", "Rebuild All")

    # Wait for, and test if the build succeeded
    waitFor("buildFinished == True", 300000)
    test.verify(buildSucceeded == 1)

    invokeMenuItem("File", "Exit")

def init():
    global SpeedCrunchPath
    SpeedCrunchPath = SDKPath + "/creator-test-data/speedcrunch/src/CMakeLists.txt"
    cleanup()

def cleanup():
    # Make sure the .user files are gone
    if os.access(SpeedCrunchPath + ".user", os.F_OK):
        os.remove(SpeedCrunchPath + ".user")

    BuildPath = SDKPath + "/creator-test-data/speedcrunch/src/qtcreator-build"

    if os.access(BuildPath, os.F_OK):
        shutil.rmtree(BuildPath)